# AR/VR Technology for ResilienceAI

## Executive Summary

AR/VR technology offers transformative potential for ResilienceAI by enabling immersive data visualization, 3D geospatial exploration, and realistic training simulations. This document provides a comprehensive analysis of AR/VR architecture, implementation patterns, and integration strategies for building next-generation disaster management and climate resilience applications.

---

## 1. AR/VR Architecture Overview

### 1.1 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RESILIENCEAI AR/VR PLATFORM                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      PRESENTATION LAYER                              │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │   │
│  │  │   WebXR      │  │   Unity      │  │   Unreal     │  │ Native   │ │   │
│  │  │   (Web)      │  │   (Mobile)   │  │   (Desktop)  │  │   AR     │ │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └──────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      SPATIAL COMPUTING LAYER                         │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │   │
│  │  │   3D Engine  │  │   Physics    │  │   Spatial  │  │ Gesture  │ │   │
│  │  │   (Three.js/ │  │   Simulation │  │   Mapping  │  │ Recognition│ │   │
│  │  │   Babylon)   │  │              │  │              │  │          │ │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └──────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      DATA & ANALYTICS LAYER                          │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │   │
│  │  │  Geospatial  │  │   Real-time  │  │   ML/AI      │  │ Analytics│ │   │
│  │  │   Services   │  │   Data Stream│  │   Models     │  │ Engine   │ │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └──────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      INFRASTRUCTURE LAYER                            │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │   │
│  │  │   Cloud      │  │   Edge       │  │   CDN        │  │ 5G/IoT   │ │   │
│  │  │   Services   │  │   Computing  │  │   Network    │  │ Gateway  │ │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └──────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Core Components

| Component | Technology | Purpose | Platform |
|-----------|-----------|---------|----------|
| 3D Rendering Engine | Three.js / Babylon.js | Web-based 3D visualization | WebXR |
| Game Engine | Unity 2023+ / Unreal Engine 5 | High-fidelity experiences | Mobile, Desktop, VR |
| Spatial Mapping | ARKit / ARCore / OpenXR | Environment understanding | Mobile AR, Headsets |
| Physics Engine | PhysX / Havok / Cannon.js | Realistic simulations | All platforms |
| Networking | Photon / Mirror / WebRTC | Multi-user collaboration | All platforms |
| Geospatial | CesiumJS / Mapbox GL | 3D map integration | Web, Mobile |

---

## 2. Technology Stack Comparison

### 2.1 Platform Comparison Matrix

| Feature | WebXR | Unity | Unreal Engine | Native AR |
|---------|-------|-------|---------------|-----------|
| **Development Speed** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Performance** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Cross-Platform** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **3D Quality** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Deployment** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Learning Curve** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Cost** | Free | Free/Paid | 5% Revenue | Free |

### 2.2 Recommended Stack by Use Case

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RECOMMENDED TECHNOLOGY STACK                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  USE CASE: Web-based Dashboard & Quick Prototyping                          │
│  ├── WebXR (Three.js + WebXR Device API)                                    │
│  ├── CesiumJS for 3D geospatial                                             │
│  ├── D3.js for data visualization                                           │
│  └── Progressive Web App (PWA) deployment                                   │
│                                                                             │
│  USE CASE: Mobile AR Field Applications                                     │
│  ├── Unity 2023 LTS with AR Foundation                                      │
│  ├── ARCore (Android) / ARKit (iOS)                                         │
│  ├── Mapbox Unity SDK                                                       │
│  └── Firebase for backend                                                   │
│                                                                             │
│  USE CASE: High-Fidelity Training Simulation                                │
│  ├── Unreal Engine 5                                                        │
│  ├── MetaHuman for realistic characters                                     │
│  ├── NVIDIA Omniverse for physics                                           │
│  └── Varjo / HTC Vive Pro 2 for headsets                                    │
│                                                                             │
│  USE CASE: Multi-User Collaboration                                         │
│  ├── Unity with Photon PUN/Fusion                                           │
│  ├── Spatial Anchors for shared reference                                   │
│  ├── Voice chat (Vivox / Agora)                                             │
│  └── Cloud anchors (ARCore/ARKit)                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. WebXR Implementation

### 3.1 WebXR Architecture for ResilienceAI

```javascript
// File: /src/ar-vr/webxr/ResilienceXR.js

/**
 * ResilienceXR - Core WebXR Manager for ResilienceAI
 * Handles session management, rendering, and interaction
 */

class ResilienceXR {
  constructor(canvasId, options = {}) {
    this.canvas = document.getElementById(canvasId);
    this.renderer = null;
    this.scene = null;
    this.camera = null;
    this.xrSession = null;
    this.xrReferenceSpace = null;
    this.isXRMode = false;
    
    this.config = {
      enableHandTracking: options.enableHandTracking || false,
      enableSpatialAudio: options.enableSpatialAudio || true,
      renderScale: options.renderScale || 1.0,
      antialias: options.antialias !== false,
      ...options
    };
    
    this.callbacks = {
      onSessionStarted: options.onSessionStarted || (() => {}),
      onSessionEnded: options.onSessionEnded || (() => {}),
      onSelect: options.onSelect || (() => {}),
      onSqueeze: options.onSqueeze || (() => {})
    };
    
    this.init();
  }
  
  async init() {
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x1a1a2e);
    
    this.camera = new THREE.PerspectiveCamera(
      75, window.innerWidth / window.innerHeight, 0.1, 1000
    );
    this.camera.position.set(0, 1.6, 3);
    
    this.renderer = new THREE.WebGLRenderer({
      canvas: this.canvas,
      antialias: this.config.antialias,
      alpha: true
    });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.xr.enabled = true;
    
    this.setupLighting();
    this.setupEnvironment();
    window.addEventListener('resize', () => this.onWindowResize());
  }
  
  setupLighting() {
    const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
    this.scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(10, 20, 10);
    directionalLight.castShadow = true;
    this.scene.add(directionalLight);
    
    const hemiLight = new THREE.HemisphereLight(0x87ceeb, 0x362d1d, 0.5);
    this.scene.add(hemiLight);
  }
  
  setupEnvironment() {
    const groundGeometry = new THREE.PlaneGeometry(100, 100);
    const groundMaterial = new THREE.MeshStandardMaterial({
      color: 0x2d4a3e, roughness: 0.8, metalness: 0.1
    });
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    this.scene.add(ground);
    
    const gridHelper = new THREE.GridHelper(100, 50, 0x444444, 0x222222);
    this.scene.add(gridHelper);
  }
  
  static async isSupported(mode = 'immersive-vr') {
    if (!navigator.xr) return { supported: false, reason: 'WebXR not available' };
    try {
      const supported = await navigator.xr.isSessionSupported(mode);
      return { supported, reason: supported ? null : 'Session mode not supported' };
    } catch (error) {
      return { supported: false, reason: error.message };
    }
  }
  
  async startXR(mode = 'immersive-vr') {
    const check = await ResilienceXR.isSupported(mode);
    if (!check.supported) throw new Error(`WebXR not supported: ${check.reason}`);
    
    const sessionInit = {
      requiredFeatures: ['local-floor'],
      optionalFeatures: ['hand-tracking', 'layers']
    };
    
    this.xrSession = await navigator.xr.requestSession(mode, sessionInit);
    this.xrReferenceSpace = await this.xrSession.requestReferenceSpace('local-floor');
    this.setupInputHandling();
    this.renderer.xr.setSession(this.xrSession);
    this.xrSession.addEventListener('end', () => this.onSessionEnded());
    this.isXRMode = true;
    this.callbacks.onSessionStarted(this.xrSession);
    this.renderer.setAnimationLoop((time, frame) => this.render(time, frame));
  }
  
  setupInputHandling() {
    this.xrSession.addEventListener('select', (event) => {
      const frame = event.frame;
      const pose = frame.getPose(event.inputSource.targetRaySpace, this.xrReferenceSpace);
      if (pose) this.callbacks.onSelect({ position: pose.transform.position, inputSource: event.inputSource });
    });
    this.xrSession.addEventListener('squeeze', (event) => {
      this.callbacks.onSqueeze({ inputSource: event.inputSource });
    });
  }
  
  render(time, frame) {
    if (frame) {
      const pose = frame.getViewerPose(this.xrReferenceSpace);
      if (pose && this.config.enableSpatialAudio) this.updateSpatialAudio(pose.transform.position);
    }
    this.renderer.render(this.scene, this.camera);
  }
  
  onSessionEnded() {
    this.isXRMode = false;
    this.xrSession = null;
    this.renderer.setAnimationLoop(null);
    this.callbacks.onSessionEnded();
    this.animate();
  }
  
  animate() {
    if (!this.isXRMode) {
      requestAnimationFrame(() => this.animate());
      this.renderer.render(this.scene, this.camera);
    }
  }
  
  onWindowResize() {
    if (!this.isXRMode) {
      this.camera.aspect = window.innerWidth / window.innerHeight;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(window.innerWidth, window.innerHeight);
    }
  }
}

export default ResilienceXR;
```

### 3.2 Geospatial Visualization Component

```javascript
// File: /src/ar-vr/webxr/GeospatialXR.js

class GeospatialXR {
  constructor(resilienceXR, options = {}) {
    this.xr = resilienceXR;
    this.options = {
      cesiumIonToken: options.cesiumIonToken || '',
      terrainExaggeration: options.terrainExaggeration || 1.0,
      ...options
    };
    this.tilesets = new Map();
    this.dataLayers = new Map();
    this.init();
  }
  
  async init() {
    await this.initializeCesium();
    this.setupTerrainRendering();
    this.setupDataLayers();
  }
  
  setupTerrainRendering() {
    const terrainMaterial = new THREE.ShaderMaterial({
      uniforms: {
        uElevationScale: { value: this.options.terrainExaggeration },
        uWaterLevel: { value: 0.0 }
      },
      vertexShader: `
        uniform float uElevationScale;
        varying float vElevation;
        void main() {
          vElevation = position.y * uElevationScale;
          vec3 newPosition = position;
          newPosition.y = vElevation;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(newPosition, 1.0);
        }
      `,
      fragmentShader: `
        uniform float uWaterLevel;
        varying float vElevation;
        void main() {
          vec3 lowColor = vec3(0.18, 0.29, 0.24);
          vec3 midColor = vec3(0.45, 0.45, 0.33);
          vec3 highColor = vec3(0.95, 0.95, 0.95);
          vec3 waterColor = vec3(0.13, 0.42, 0.60);
          vec3 color = vElevation < uWaterLevel ? waterColor : 
                       vElevation < 100.0 ? mix(lowColor, midColor, vElevation / 100.0) :
                       mix(midColor, highColor, (vElevation - 100.0) / 400.0);
          gl_FragColor = vec4(color, 1.0);
        }
      `,
      side: THREE.DoubleSide
    });
    
    const terrainGeometry = new THREE.PlaneGeometry(10000, 10000, 256, 256);
    this.terrainMesh = new THREE.Mesh(terrainGeometry, terrainMaterial);
    this.terrainMesh.rotation.x = -Math.PI / 2;
    this.xr.addObject(this.terrainMesh);
  }
  
  addHazardVisualization(hazardData, type = 'flood') {
    const hazardGroup = new THREE.Group();
    if (type === 'flood') this.createFloodVisualization(hazardGroup, hazardData);
    else if (type === 'fire') this.createFireVisualization(hazardGroup, hazardData);
    this.xr.addObject(hazardGroup);
    return hazardGroup;
  }
  
  createFloodVisualization(group, data) {
    data.zones.forEach(zone => {
      const geometry = new THREE.PlaneGeometry(zone.width, zone.depth);
      const material = new THREE.MeshPhysicalMaterial({
        color: 0x0066cc, transparent: true, opacity: 0.6, transmission: 0.5
      });
      const water = new THREE.Mesh(geometry, material);
      water.rotation.x = -Math.PI / 2;
      water.position.set(zone.x, zone.waterLevel, zone.z);
      this.animateWater(water);
      group.add(water);
    });
  }
  
  animateWater(waterMesh) {
    const originalY = waterMesh.position.y;
    const animate = () => {
      waterMesh.position.y = originalY + Math.sin(Date.now() * 0.001) * 0.1;
      requestAnimationFrame(animate);
    };
    animate();
  }
}

export { GeospatialXR };
```

---

## 4. Unity Implementation for Mobile AR

### 4.1 Unity AR Foundation Architecture

```csharp
// File: /src/ar-vr/unity/Scripts/ResilienceARManager.cs

using UnityEngine;
using UnityEngine.XR.ARFoundation;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace ResilienceAI.AR
{
    public class ResilienceARManager : MonoBehaviour
    {
        [Header("AR Components")]
        [SerializeField] private ARSession arSession;
        [SerializeField] private ARSessionOrigin sessionOrigin;
        [SerializeField] private ARPlaneManager planeManager;
        [SerializeField] private ARRaycastManager raycastManager;
        [SerializeField] private ARAnchorManager anchorManager;
        
        [Header("Prefabs")]
        [SerializeField] private GameObject hazardIndicatorPrefab;
        [SerializeField] private GameObject infrastructureMarkerPrefab;
        
        private bool isSessionActive = false;
        private List<ARAnchor> placedAnchors = new List<ARAnchor>();
        
        public static ResilienceARManager Instance { get; private set; }
        
        private void Awake()
        {
            if (Instance == null) { Instance = this; DontDestroyOnLoad(gameObject); }
            else Destroy(gameObject);
        }
        
        private async void Start()
        {
            if (ARSession.state == ARSessionState.None || ARSession.state == ARSessionState.Unsupported)
            { Debug.LogError("AR not supported"); return; }
            
            while (ARSession.state < ARSessionState.Ready) await Task.Delay(100);
            
            planeManager.requestedDetectionMode = PlaneDetectionMode.Horizontal | PlaneDetectionMode.Vertical;
            planeManager.planesChanged += OnPlanesChanged;
            isSessionActive = true;
        }
        
        private void OnPlanesChanged(ARPlanesChangedEventArgs args)
        {
            foreach (var plane in args.added)
            {
                var renderer = plane.GetComponent<MeshRenderer>();
                if (renderer) renderer.material.color = GetPlaneColor(plane.classification);
            }
        }
        
        private Color GetPlaneColor(PlaneClassification c) => c switch
        {
            PlaneClassification.Floor => new Color(0.2f, 0.8f, 0.2f, 0.3f),
            PlaneClassification.Wall => new Color(0.8f, 0.2f, 0.2f, 0.3f),
            _ => new Color(0.5f, 0.5f, 0.5f, 0.3f)
        };
        
        public bool PlaceObject(Vector2 screenPos, GameObject prefab, out GameObject obj, out ARAnchor anchor)
        {
            obj = null; anchor = null;
            List<ARRaycastHit> hits = new List<ARRaycastHit>();
            if (!raycastManager.Raycast(screenPos, hits, TrackableType.PlaneWithinPolygon)) return false;
            
            var hit = hits[0];
            var anchorObj = anchorManager.AttachAnchor(hit.trackable as ARPlane, hit.pose);
            if (anchorObj == null) return false;
            
            obj = Instantiate(prefab, anchorObj.transform);
            obj.transform.localPosition = Vector3.zero;
            anchor = anchorObj;
            placedAnchors.Add(anchor);
            return true;
        }
    }
    
    public enum HazardSeverity { Low, Medium, High, Critical }
    
    [System.Serializable]
    public class HazardData
    {
        public string id, type, description;
        public HazardSeverity severity;
        public Vector3 location;
        public float radius;
    }
}
```

---

## 5. Unreal Engine VR Training

### 5.1 VR Training Manager Header

```cpp
// File: /src/ar-vr/unreal/Source/ResilienceVR/ResilienceVRManager.h

#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ResilienceVRManager.generated.h"

UENUM(BlueprintType)
enum class EVRScenarioType : uint8
{
    FloodResponse, FireEvacuation, EarthquakeSafety,
    HurricanePrep, SearchAndRescue, MedicalEmergency
};

USTRUCT(BlueprintType)
struct FVRScenarioConfig
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere) EVRScenarioType ScenarioType;
    UPROPERTY(EditAnywhere) float TimeLimit;
    UPROPERTY(EditAnywhere) int32 MaxParticipants;
    UPROPERTY(EditAnywhere) bool bEnableHapticFeedback;
};

USTRUCT(BlueprintType)
struct FVRPerformanceMetrics
{
    GENERATED_BODY()
    UPROPERTY() float CompletionTime;
    UPROPERTY() int32 Score;
    UPROPERTY() int32 MistakesMade;
    UPROPERTY() float Accuracy;
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnScenarioStarted, const FVRScenarioConfig&, Config);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnScenarioCompleted, const FVRPerformanceMetrics&, Metrics);

UCLASS()
class RESILIENCEVR_API AResilienceVRManager : public AActor
{
    GENERATED_BODY()
    
public:
    AResilienceVRManager();
    virtual void Tick(float DeltaTime) override;
    
    UFUNCTION(BlueprintCallable) void StartScenario(const FVRScenarioConfig& Config);
    UFUNCTION(BlueprintCallable) void PauseScenario();
    UFUNCTION(BlueprintCallable) void EndScenario(bool bSuccess);
    
    UPROPERTY(BlueprintAssignable) FOnScenarioStarted OnScenarioStarted;
    UPROPERTY(BlueprintAssignable) FOnScenarioCompleted OnScenarioCompleted;
    
protected:
    UPROPERTY() bool bScenarioActive;
    UPROPERTY() bool bScenarioPaused;
    UPROPERTY() float ElapsedTime;
    UPROPERTY() int32 CurrentScore;
    UPROPERTY() FVRScenarioConfig CurrentConfig;
    UPROPERTY() FVRPerformanceMetrics CurrentMetrics;
    
    void SpawnScenarioElements();
    void UpdateScenario(float DeltaTime);
    void EvaluatePerformance();
};
```

### 5.2 VR Training Manager Implementation

```cpp
// File: /src/ar-vr/unreal/Source/ResilienceVR/ResilienceVRManager.cpp

#include "ResilienceVRManager.h"

AResilienceVRManager::AResilienceVRManager()
{
    PrimaryActorTick.bCanEverTick = true;
    bScenarioActive = false;
}

void AResilienceVRManager::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    if (bScenarioActive && !bScenarioPaused) UpdateScenario(DeltaTime);
}

void AResilienceVRManager::StartScenario(const FVRScenarioConfig& Config)
{
    if (bScenarioActive) return;
    CurrentConfig = Config;
    bScenarioActive = true;
    ElapsedTime = 0;
    CurrentScore = 0;
    SpawnScenarioElements();
    OnScenarioStarted.Broadcast(Config);
}

void AResilienceVRManager::SpawnScenarioElements()
{
    switch (CurrentConfig.ScenarioType)
    {
    case EVRScenarioType::FloodResponse:
        // Spawn flooded environment, water effects, rescue targets
        break;
    case EVRScenarioType::FireEvacuation:
        // Spawn building with fire, smoke, evacuation routes
        break;
    case EVRScenarioType::EarthquakeSafety:
        // Spawn damaged building, debris, survivors
        break;
    }
}

void AResilienceVRManager::UpdateScenario(float DeltaTime)
{
    ElapsedTime += DeltaTime;
    if (CurrentConfig.TimeLimit > 0 && ElapsedTime >= CurrentConfig.TimeLimit)
        EndScenario(false);
}

void AResilienceVRManager::EndScenario(bool bSuccess)
{
    if (!bScenarioActive) return;
    bScenarioActive = false;
    EvaluatePerformance();
    if (bSuccess) OnScenarioCompleted.Broadcast(CurrentMetrics);
}

void AResilienceVRManager::EvaluatePerformance()
{
    CurrentMetrics.CompletionTime = ElapsedTime;
    CurrentMetrics.Score = CurrentScore;
}
```

---

## 6. Interaction Design

### 6.1 VR Interaction System

```csharp
// File: /src/ar-vr/unity/Scripts/VRInteractionSystem.cs

using UnityEngine;
using UnityEngine.XR.Interaction.Toolkit;

namespace ResilienceAI.AR
{
    public class VRInteractionSystem : MonoBehaviour
    {
        [SerializeField] private XRRayInteractor leftRay, rightRay;
        [SerializeField] private XRDirectInteractor leftDirect, rightDirect;
        [SerializeField] private LineRenderer leftVisual, rightVisual;
        
        public enum Mode { Direct, Ray, Teleport, UI }
        private Mode currentMode = Mode.Ray;
        
        void Start()
        {
            SubscribeToEvents();
        }
        
        void SubscribeToEvents()
        {
            leftRay.hoverEntered.AddListener(OnHover);
            leftRay.selectEntered.AddListener(OnSelect);
            rightRay.hoverEntered.AddListener(OnHover);
            rightRay.selectEntered.AddListener(OnSelect);
        }
        
        void OnHover(HoverEnterEventArgs args)
        {
            var controller = args.interactor.GetComponent<XRBaseController>();
            controller?.SendHapticImpulse(0.5f, 0.1f);
        }
        
        void OnSelect(SelectEnterEventArgs args)
        {
            var controller = args.interactor.GetComponent<XRBaseController>();
            controller?.SendHapticImpulse(0.8f, 0.2f);
        }
        
        public void SetMode(Mode mode)
        {
            currentMode = mode;
            leftDirect.enabled = rightDirect.enabled = (mode == Mode.Direct);
            leftRay.enabled = rightRay.enabled = (mode == Mode.Ray);
        }
    }
}
```

---

## 7. Performance Optimization

### 7.1 Performance Guidelines

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     PERFORMANCE OPTIMIZATION GUIDELINES                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  TARGET FRAME RATES                                                         │
│  ├── VR Headsets (Quest 2/3, PSVR2): 72-120 FPS                            │
│  ├── Mobile AR: 30-60 FPS                                                   │
│  ├── WebXR: 60-90 FPS (depending on device)                                │
│  └── Desktop VR (Index, Vive Pro 2): 90-144 FPS                            │
│                                                                             │
│  POLYGON BUDGETS                                                            │
│  ├── Mobile AR: 50,000-100,000 triangles per frame                         │
│  ├── Standalone VR: 100,000-200,000 triangles per frame                    │
│  ├── PC VR: 500,000-1,000,000 triangles per frame                          │
│  └── WebXR: 50,000-100,000 triangles per frame                             │
│                                                                             │
│  TEXTURE GUIDELINES                                                         │
│  ├── Max texture size: 2048x2048 (mobile), 4096x4096 (PC)                  │
│  ├── Use texture atlasing to reduce draw calls                             │
│  ├── Compress textures: ASTC (mobile), DXT (PC)                            │
│  └── Use mipmaps for all textures                                          │
│                                                                             │
│  OPTIMIZATION TECHNIQUES                                                    │
│  ├── Batch static geometry                                                   │
│  ├── Use GPU instancing for repeated objects                                │
│  ├── Implement LOD (Level of Detail) system                                 │
│  ├── Pool frequently instantiated objects                                   │
│  └── Use object culling (frustum, occlusion)                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Performance Monitor

```javascript
// File: /src/ar-vr/webxr/PerformanceMonitor.js

class PerformanceMonitor {
  constructor(options = {}) {
    this.options = { targetFPS: 72, warningThreshold: 0.8, sampleSize: 60, ...options };
    this.frameTimes = [];
    this.currentFPS = 0;
    this.isMonitoring = false;
  }
  
  start(renderer, scene) {
    this.renderer = renderer;
    this.scene = scene;
    this.isMonitoring = true;
    this.lastFrameTime = performance.now();
    this.monitorLoop();
  }
  
  monitorLoop() {
    if (!this.isMonitoring) return;
    const now = performance.now();
    const frameTime = now - this.lastFrameTime;
    this.lastFrameTime = now;
    
    this.currentFPS = 1000 / frameTime;
    this.frameTimes.push(frameTime);
    if (this.frameTimes.length > this.options.sampleSize) this.frameTimes.shift();
    
    this.checkPerformanceIssues(frameTime);
    requestAnimationFrame(() => this.monitorLoop());
  }
  
  checkPerformanceIssues(frameTime) {
    const targetFrameTime = 1000 / this.options.targetFPS;
    if (frameTime > targetFrameTime / this.options.warningThreshold) {
      console.warn('Performance warning: Low FPS', { currentFPS: this.currentFPS });
    }
  }
  
  getReport() {
    const avgTime = this.frameTimes.reduce((a, b) => a + b, 0) / this.frameTimes.length;
    return {
      fps: { current: Math.round(this.currentFPS), average: Math.round(1000 / avgTime) },
      quality: this.currentFPS / this.options.targetFPS >= 0.95 ? 'excellent' :
               this.currentFPS / this.options.targetFPS >= 0.8 ? 'good' :
               this.currentFPS / this.options.targetFPS >= 0.6 ? 'fair' : 'poor'
    };
  }
}

export default PerformanceMonitor;
```

---

## 8. Headset Support Matrix

| Device | Type | Resolution | Refresh Rate | Tracking | Hand Tracking | Platform |
|--------|------|------------|--------------|----------|---------------|----------|
| Meta Quest 3 | Standalone VR | 2064×2208 | 72-120Hz | Inside-out | Yes | Android |
| Meta Quest 2 | Standalone VR | 1832×1920 | 72-120Hz | Inside-out | Yes | Android |
| Apple Vision Pro | Mixed Reality | 3660×3200 | 90-100Hz | Inside-out | Yes | visionOS |
| HTC Vive Pro 2 | Tethered VR | 2448×2448 | 90-120Hz | Lighthouse | No | PC |
| Valve Index | Tethered VR | 1440×1600 | 80-144Hz | Lighthouse | No | PC |
| PSVR2 | Console VR | 2000×2040 | 90-120Hz | Inside-out | Yes | PS5 |
| HoloLens 2 | Mixed Reality | 1440×936 | 60Hz | Inside-out | Yes | Windows |

---

## 9. Use Case Analysis

| Use Case | Technology | Platform | Priority | Impact |
|----------|-----------|----------|----------|--------|
| **Field Assessment** | Mobile AR | iOS/Android | High | On-site hazard visualization |
| **Command Center** | WebXR + VR | Web + Headsets | High | Immersive situational awareness |
| **Training Simulations** | VR | Quest/PC VR | High | Cost-effective training |
| **Public Education** | Mobile AR | iOS/Android | Medium | Community engagement |
| **Remote Collaboration** | WebXR | Web | Medium | Multi-user coordination |
| **Disaster Replay** | VR | PC VR | Medium | Post-event analysis |

---

## 10. Implementation Priority

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    IMPLEMENTATION PRIORITY ORDER                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PHASE 1: FOUNDATION (Months 1-3)                                          │
│  ├── 1. WebXR Dashboard with 3D geospatial (Three.js + CesiumJS)          │
│  ├── 2. Mobile AR Field App (Unity + AR Foundation)                       │
│  └── 3. Basic training module (WebXR)                                     │
│                                                                             │
│  PHASE 2: ENHANCEMENT (Months 4-6)                                         │
│  ├── 4. VR Training Platform (Unity/Unreal + Quest)                       │
│  ├── 5. Multi-user collaboration (Photon/Normcore)                        │
│  └── 6. Advanced geospatial (Real-time streaming)                         │
│                                                                             │
│  PHASE 3: ADVANCED (Months 7-12)                                           │
│  ├── 7. Full VR simulation suite (AI-driven NPCs)                         │
│  ├── 8. Mixed reality command center (Vision Pro + HoloLens)              │
│  └── 9. AI-powered assistance (Voice commands)                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 11. Integration Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RESILIENCEAI AR/VR INTEGRATION                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      RESILIENCEAI CORE API                           │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │   │
│  │  │ Hazard   │  │ Resource │  │ Weather  │  │ Alert    │            │   │
│  │  │ Service  │  │ Service  │  │ Service  │  │ Service  │            │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      AR/VR ADAPTER LAYER                             │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │   │
│  │  │ Data     │  │ Spatial  │  │ Event    │  │ User     │            │   │
│  │  │ Adapter  │  │ Adapter  │  │ Adapter  │  │ Adapter  │            │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│              ┌─────────────────────┼─────────────────────┐                 │
│              ▼                     ▼                     ▼                 │
│  ┌───────────────┐      ┌───────────────┐      ┌───────────────┐          │
│  │   WebXR       │      │   Unity AR    │      │   Unreal VR   │          │
│  │   Client      │      │   Client      │      │   Client      │          │
│  └───────────────┘      └───────────────┘      └───────────────┘          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 12. Integration Adapter

```javascript
// File: /src/ar-vr/integration/ResilienceAIAdapter.js

class ResilienceAIAdapter {
  constructor(apiEndpoint, options = {}) {
    this.apiEndpoint = apiEndpoint;
    this.options = { updateInterval: 5000, enableRealtime: true, ...options };
    this.callbacks = new Map();
    this.cache = new Map();
  }
  
  async initialize() {
    if (this.options.enableRealtime) await this.connectRealtime();
    setInterval(() => this.updateCache(), this.options.updateInterval);
  }
  
  async connectRealtime() {
    this.eventSource = new EventSource(`${this.apiEndpoint}/events`);
    this.eventSource.onmessage = (e) => this.handleEvent(JSON.parse(e.data));
    this.eventSource.onerror = () => setTimeout(() => this.connectRealtime(), 5000);
  }
  
  handleEvent(event) {
    const handlers = { hazard_update: 'hazard', resource_update: 'resource', 
                       weather_update: 'weather', alert: 'alert' };
    if (handlers[event.type]) this.notify(handlers[event.type], event.data);
  }
  
  subscribe(type, cb) {
    if (!this.callbacks.has(type)) this.callbacks.set(type, []);
    this.callbacks.get(type).push(cb);
    return () => { const arr = this.callbacks.get(type); arr.splice(arr.indexOf(cb), 1); };
  }
  
  notify(type, data) {
    (this.callbacks.get(type) || []).forEach(cb => { try { cb(data); } catch(e) {} });
  }
  
  async fetchHazards(bounds) {
    const res = await fetch(`${this.apiEndpoint}/hazards`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ bounds })
    });
    return res.json();
  }
  
  async reportObservation(obs) {
    const res = await fetch(`${this.apiEndpoint}/observations`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(obs)
    });
    return res.json();
  }
  
  updateCache() {
    for (const [k, v] of this.cache.entries()) {
      if (v.timestamp && Date.now() - v.timestamp > 60000) this.cache.delete(k);
    }
  }
}

export default ResilienceAIAdapter;
```

---

## 13. UX Principles

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AR/VR USER EXPERIENCE PRINCIPLES                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. COMFORT & SAFETY                                                        │
│  ├── Maintain 60+ FPS at all times                                         │
│  ├── Minimize camera movement and acceleration                             │
│  ├── Provide comfort options (teleport vs smooth locomotion)               │
│  └── Include regular break reminders                                       │
│                                                                             │
│  2. INTUITIVE INTERACTION                                                   │
│  ├── Use natural gestures and movements                                    │
│  ├── Provide clear visual feedback for all interactions                    │
│  ├── Support multiple interaction methods                                  │
│  └── Include haptic feedback where available                               │
│                                                                             │
│  3. INFORMATION HIERARCHY                                                   │
│  ├── Keep critical information in comfortable viewing area                 │
│  ├── Use depth and scale to convey importance                              │
│  ├── Minimize UI elements in immersive views                               │
│  └── Use spatial audio for alerts and notifications                        │
│                                                                             │
│  4. ACCESSIBILITY                                                           │
│  ├── Support multiple locomotion options                                   │
│  ├── Include text-to-speech and speech-to-text                             │
│  ├── Provide adjustable text sizes and contrast                            │
│  └── Support colorblind-friendly palettes                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 14. Cost Considerations

| Component | WebXR | Unity | Unreal | Notes |
|-----------|-------|-------|--------|-------|
| **Development License** | Free | Free (<$100K) | 5% after $1M | Unity Pro: $2,040/yr |
| **Target Hardware** | $0 | $299-$999 | $999-$1,499 | Quest 3, PC VR |
| **Asset Store** | $0-$500 | $0-$2,000 | $0-$2,000 | Models, textures |
| **Backend Services** | $50-$500/mo | $50-$500/mo | $50-$500/mo | Photon, PlayFab |
| **Testing Devices** | $0 | $600-$3,000 | $1,500-$3,000 | Multiple headsets |
| **Total Est. (Year 1)** | $1,000-$5,000 | $5,000-$15,000 | $10,000-$25,000 | Small-medium |

---

## 15. Conclusion

AR/VR technology offers significant opportunities for ResilienceAI to enhance disaster management through:

1. **Immersive data visualization** - 3D geospatial exploration of hazard data
2. **Realistic training simulations** - Cost-effective, repeatable training scenarios
3. **Improved field coordination** - Mobile AR for on-site assessment

**Recommended Approach:**
1. Start with WebXR for rapid prototyping and broad accessibility
2. Develop Unity-based mobile AR for field operations
3. Build VR training simulations using Unity or Unreal Engine
4. Integrate all platforms through a unified backend adapter
5. Iterate based on user feedback and performance metrics

**Key Success Factors:**
- Maintain 60+ FPS performance
- Intuitive interaction design
- Seamless ResilienceAI backend integration
- Comprehensive cross-device testing

---

## 16. References

- [WebXR Device API](https://immersive-web.github.io/webxr/)
- [Unity AR Foundation](https://docs.unity3d.com/Packages/com.unity.xr.arfoundation@5.0/manual/index.html)
- [Unreal Engine VR Development](https://docs.unrealengine.com/5.0/en-US/developing-for-vr-in-unreal-engine/)
- [OpenXR Specification](https://www.khronos.org/openxr/)
- [Three.js](https://threejs.org/)
- [CesiumJS](https://cesium.com/platform/cesiumjs/)
