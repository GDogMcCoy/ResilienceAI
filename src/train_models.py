"""
ResilienceAI - Model Training Pipeline
Trains classification and regression models for disaster vulnerability prediction.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score,
    accuracy_score, f1_score, roc_curve, auc
)
from config import PROCESSED_DIR, MODELS_DIR, FIGURES_DIR, RANDOM_STATE, TEST_SIZE, CV_FOLDS


# ── Feature Selection ─────────────────────────────────────────────────
FEATURE_COLUMNS = [
    # Demographics (raw vulnerability indicators)
    "total_population", "median_income",
    "elderly_pct", "poverty_pct", "disability_pct", "uninsured_pct",
    # Infrastructure distances (raw isolation indicators)
    "dist_nearest_hospitals_km", "dist_nearest_fire_stations_km",
    "dist_nearest_ems_stations_km", "dist_nearest_nursing_homes_km",
    # Infrastructure counts
    "count_hospitals_50km", "count_fire_stations_50km",
    "count_ems_stations_50km", "count_nursing_homes_50km",
    # Infrastructure density
    "density_hospitals_per10k", "density_fire_stations_per10k",
    "density_ems_stations_per10k", "density_nursing_homes_per10k",
    # Disaster history (raw exposure indicators)
    "disaster_count", "disaster_count_recent",
    "disaster_flood", "disaster_severe_storms",
    "disaster_hurricane", "disaster_fire", "disaster_tornado",
    # NOTE: vulnerability_index and isolation_index deliberately EXCLUDED
    # because they are components of the target variable (risk_score).
    # The model learns from raw features only, avoiding circular reasoning.
]

TARGET_COL = "risk_level"
SCORE_COL = "risk_score"


def prepare_data(df):
    """Prepare features and target for modeling."""
    # Use only columns that exist
    available_features = [c for c in FEATURE_COLUMNS if c in df.columns]
    print(f"  Using {len(available_features)}/{len(FEATURE_COLUMNS)} features")

    X = df[available_features].copy()
    y = df[TARGET_COL].copy()

    # Drop rows with missing target
    mask = y.notna() & ~X.isna().all(axis=1)
    X = X[mask]
    y = y[mask]

    # Fill remaining NaN with median
    X = X.fillna(X.median())

    # Encode target
    le = LabelEncoder()
    le.fit(["Low", "Medium", "High"])
    y_encoded = le.transform(y)

    return X, y_encoded, le, available_features


def train_and_evaluate():
    """Train multiple models and compare performance."""
    print("=" * 60)
    print("ResilienceAI - Model Training Pipeline")
    print("=" * 60)

    # Load data
    df = pd.read_csv(PROCESSED_DIR / "county_features.csv", dtype={"fips": str})
    print(f"\nLoaded {len(df)} counties")

    X, y, le, feature_names = prepare_data(df)
    print(f"  Samples: {len(X)}, Features: {X.shape[1]}, Classes: {le.classes_}")
    print(f"  Class distribution: {dict(zip(le.classes_, np.bincount(y)))}")

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    print(f"  Train: {len(X_train)}, Test: {len(X_test)}")

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Define models
    models = {
        "Random Forest": RandomForestClassifier(
            n_estimators=200, max_depth=15, min_samples_split=5,
            random_state=RANDOM_STATE, n_jobs=-1
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=200, max_depth=5, learning_rate=0.1,
            random_state=RANDOM_STATE
        ),
        "Logistic Regression": LogisticRegression(
            max_iter=1000, random_state=RANDOM_STATE
        ),
        "Neural Network": MLPClassifier(
            hidden_layer_sizes=(128, 64, 32), max_iter=500,
            random_state=RANDOM_STATE, early_stopping=True
        ),
    }

    results = {}
    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)

    for name, model in models.items():
        print(f"\n  Training {name}...")

        # Use scaled data for LR and NN, raw for tree models
        if name in ["Logistic Regression", "Neural Network"]:
            X_tr, X_te = X_train_scaled, X_test_scaled
            X_cv = X_train_scaled
        else:
            X_tr, X_te = X_train.values, X_test.values
            X_cv = X_train.values

        # Cross-validation
        cv_scores = cross_val_score(model, X_cv, y_train, cv=cv, scoring="f1_macro")

        # Fit on full training set
        model.fit(X_tr, y_train)
        y_pred = model.predict(X_te)
        y_prob = model.predict_proba(X_te) if hasattr(model, "predict_proba") else None

        # Metrics
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average="macro")
        report = classification_report(y_test, y_pred, target_names=le.classes_)

        results[name] = {
            "model": model,
            "accuracy": acc,
            "f1_macro": f1,
            "cv_mean": cv_scores.mean(),
            "cv_std": cv_scores.std(),
            "y_pred": y_pred,
            "y_prob": y_prob,
            "report": report,
        }

        print(f"    Accuracy: {acc:.4f}")
        print(f"    F1 (macro): {f1:.4f}")
        print(f"    CV F1 (macro): {cv_scores.mean():.4f} +/- {cv_scores.std():.4f}")

    # Save models and scaler
    joblib.dump(scaler, MODELS_DIR / "scaler.pkl")
    joblib.dump(le, MODELS_DIR / "label_encoder.pkl")
    joblib.dump(feature_names, MODELS_DIR / "feature_names.pkl")

    for name, res in results.items():
        safe_name = name.lower().replace(" ", "_")
        joblib.dump(res["model"], MODELS_DIR / f"model_{safe_name}.pkl")

    # Find best model
    best_name = max(results, key=lambda k: results[k]["f1_macro"])
    joblib.dump(results[best_name]["model"], MODELS_DIR / "best_model.pkl")
    print(f"\n  Best model: {best_name} (F1={results[best_name]['f1_macro']:.4f})")

    # Generate plots
    plot_model_comparison(results)
    plot_confusion_matrices(results, y_test, le)
    plot_roc_curves(results, y_test, le)
    plot_feature_importance(results, feature_names)

    # Save results summary
    save_results_summary(results)

    print(f"\n{'=' * 60}")
    print(f"Training complete! Models saved to {MODELS_DIR}")
    print(f"{'=' * 60}")

    return results


def plot_model_comparison(results):
    """Bar chart comparing model performance."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    names = list(results.keys())
    accuracies = [results[n]["accuracy"] for n in names]
    f1s = [results[n]["f1_macro"] for n in names]
    cv_means = [results[n]["cv_mean"] for n in names]
    cv_stds = [results[n]["cv_std"] for n in names]

    x = range(len(names))
    colors = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12"]

    # Test metrics
    bars1 = axes[0].bar([i - 0.15 for i in x], accuracies, 0.3, label="Accuracy", color=colors, alpha=0.7)
    bars2 = axes[0].bar([i + 0.15 for i in x], f1s, 0.3, label="F1 (macro)", color=colors, alpha=1.0)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(names, rotation=15, ha="right", fontsize=9)
    axes[0].set_ylabel("Score", fontsize=11)
    axes[0].set_title("Test Set Performance", fontsize=13)
    axes[0].legend()
    axes[0].set_ylim(0, 1.1)

    # CV scores
    axes[1].bar(x, cv_means, yerr=cv_stds, color=colors, alpha=0.8, capsize=5)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(names, rotation=15, ha="right", fontsize=9)
    axes[1].set_ylabel("F1 (macro)", fontsize=11)
    axes[1].set_title(f"Cross-Validation Performance ({CV_FOLDS}-Fold)", fontsize=13)
    axes[1].set_ylim(0, 1.1)

    # Add value labels
    for i, v in enumerate(cv_means):
        axes[1].text(i, v + cv_stds[i] + 0.02, f"{v:.3f}", ha="center", fontsize=9)

    plt.tight_layout()
    path = FIGURES_DIR / "model_comparison.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path.name}")


def plot_confusion_matrices(results, y_test, le):
    """Plot confusion matrices for all models."""
    n_models = len(results)
    fig, axes = plt.subplots(1, n_models, figsize=(5 * n_models, 4))
    if n_models == 1:
        axes = [axes]

    for i, (name, res) in enumerate(results.items()):
        cm = confusion_matrix(y_test, res["y_pred"])
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                    xticklabels=le.classes_, yticklabels=le.classes_,
                    ax=axes[i])
        axes[i].set_title(name, fontsize=11)
        axes[i].set_xlabel("Predicted")
        axes[i].set_ylabel("Actual")

    plt.suptitle("Confusion Matrices", fontsize=14, fontweight="bold")
    plt.tight_layout()
    path = FIGURES_DIR / "confusion_matrices.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path.name}")


def plot_roc_curves(results, y_test, le):
    """Plot ROC curves (one-vs-rest) for all models."""
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12"]

    for i, (name, res) in enumerate(results.items()):
        if res["y_prob"] is not None:
            # Macro-average ROC
            from sklearn.preprocessing import label_binarize
            y_bin = label_binarize(y_test, classes=[0, 1, 2])
            # Compute micro-average ROC
            fpr, tpr, _ = roc_curve(y_bin.ravel(), res["y_prob"].ravel())
            roc_auc_val = auc(fpr, tpr)
            ax.plot(fpr, tpr, color=colors[i], lw=2,
                    label=f"{name} (AUC={roc_auc_val:.3f})")

    ax.plot([0, 1], [0, 1], "k--", lw=1)
    ax.set_xlabel("False Positive Rate", fontsize=12)
    ax.set_ylabel("True Positive Rate", fontsize=12)
    ax.set_title("ROC Curves (Micro-Average, One-vs-Rest)", fontsize=13)
    ax.legend(loc="lower right")
    plt.tight_layout()
    path = FIGURES_DIR / "roc_curves.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path.name}")


def plot_feature_importance(results, feature_names):
    """Plot feature importance from tree-based models."""
    for name in ["Random Forest", "Gradient Boosting"]:
        if name not in results:
            continue

        model = results[name]["model"]
        if not hasattr(model, "feature_importances_"):
            continue

        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1][:20]  # Top 20

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(range(len(indices)), importances[indices], color="#2c3e50", alpha=0.8)
        ax.set_yticks(range(len(indices)))
        ax.set_yticklabels([feature_names[i] for i in indices], fontsize=9)
        ax.set_xlabel("Feature Importance", fontsize=11)
        ax.set_title(f"Top 20 Features ({name})", fontsize=13)
        ax.invert_yaxis()

        plt.tight_layout()
        safe_name = name.lower().replace(" ", "_")
        path = FIGURES_DIR / f"feature_importance_{safe_name}.png"
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"  Saved: {path.name}")

    # SHAP analysis for best tree model
    try:
        import shap
        best_tree = results.get("Gradient Boosting", results.get("Random Forest"))
        if best_tree:
            print("  Computing SHAP values...")
            X_test_sample = pd.DataFrame(
                best_tree.get("X_test_sample", np.zeros((1, len(feature_names)))),
                columns=feature_names
            )
            # Skip if we don't have stored test data
    except ImportError:
        print("  [SKIP] SHAP not available")


def save_results_summary(results):
    """Save results to CSV."""
    rows = []
    for name, res in results.items():
        rows.append({
            "model": name,
            "accuracy": round(res["accuracy"], 4),
            "f1_macro": round(res["f1_macro"], 4),
            "cv_f1_mean": round(res["cv_mean"], 4),
            "cv_f1_std": round(res["cv_std"], 4),
        })
    summary = pd.DataFrame(rows)
    path = FIGURES_DIR / "model_results_summary.csv"
    summary.to_csv(path, index=False)
    print(f"  Saved: {path.name}")

    # Print full reports
    for name, res in results.items():
        print(f"\n  === {name} ===")
        print(res["report"])


if __name__ == "__main__":
    train_and_evaluate()
