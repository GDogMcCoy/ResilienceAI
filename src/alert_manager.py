"""
Real-Time Alert System for ResilienceAI
Manages alert subscriptions, notifications, and real-time monitoring
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
import time


@dataclass
class AlertSubscription:
    """Represents an alert subscription for a county"""
    id: str
    county_fips: str
    county_name: str
    state: str
    threshold: float
    alert_types: List[str]
    webhook_url: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    created_at: str
    last_triggered: Optional[str]
    is_active: bool
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AlertSubscription':
        return cls(**data)


@dataclass
class AlertEvent:
    """Represents a triggered alert event"""
    id: str
    subscription_id: str
    county_fips: str
    alert_type: str
    severity: str
    message: str
    data: Dict[str, Any]
    triggered_at: str
    acknowledged_at: Optional[str]
    status: str  # 'active', 'acknowledged', 'resolved'
    
    def to_dict(self) -> Dict:
        return asdict(self)


class AlertManager:
    """
    Manages real-time alert subscriptions and notifications
    """
    
    def __init__(self, db_path: str = "data/alerts.db"):
        self.db_path = db_path
        self._init_db()
        self._lock = threading.Lock()
    
    def _init_db(self):
        """Initialize SQLite database for alerts"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Subscriptions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                id TEXT PRIMARY KEY,
                county_fips TEXT NOT NULL,
                county_name TEXT NOT NULL,
                state TEXT NOT NULL,
                threshold REAL NOT NULL,
                alert_types TEXT NOT NULL,
                webhook_url TEXT,
                email TEXT,
                phone TEXT,
                created_at TEXT NOT NULL,
                last_triggered TEXT,
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        # Alert events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alert_events (
                id TEXT PRIMARY KEY,
                subscription_id TEXT NOT NULL,
                county_fips TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                data TEXT NOT NULL,
                triggered_at TEXT NOT NULL,
                acknowledged_at TEXT,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (subscription_id) REFERENCES subscriptions(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def subscribe(self, county_fips: str, county_name: str, state: str,
                  threshold: float = 0.7, alert_types: List[str] = None,
                  webhook_url: str = None, email: str = None, 
                  phone: str = None) -> str:
        """
        Create a new alert subscription
        
        Args:
            county_fips: 5-digit county FIPS code
            county_name: Name of the county
            state: State abbreviation
            threshold: Risk threshold (0-1) that triggers alerts
            alert_types: List of alert types to monitor
            webhook_url: Optional webhook URL for notifications
            email: Optional email for notifications
            phone: Optional phone for SMS notifications
            
        Returns:
            Subscription ID
        """
        import uuid
        
        subscription_id = str(uuid.uuid4())[:8]
        
        if alert_types is None:
            alert_types = ['flood', 'storm', 'drought', 'wildfire']
        
        subscription = AlertSubscription(
            id=subscription_id,
            county_fips=county_fips,
            county_name=county_name,
            state=state,
            threshold=threshold,
            alert_types=alert_types,
            webhook_url=webhook_url,
            email=email,
            phone=phone,
            created_at=datetime.now().isoformat(),
            last_triggered=None,
            is_active=True
        )
        
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO subscriptions 
                (id, county_fips, county_name, state, threshold, alert_types,
                 webhook_url, email, phone, created_at, last_triggered, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                subscription.id, subscription.county_fips, 
                subscription.county_name, subscription.state,
                subscription.threshold, json.dumps(subscription.alert_types),
                subscription.webhook_url, subscription.email, 
                subscription.phone, subscription.created_at,
                subscription.last_triggered, int(subscription.is_active)
            ))
            
            conn.commit()
            conn.close()
        
        return subscription_id
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """Deactivate a subscription"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE subscriptions SET is_active = 0 WHERE id = ?
            ''', (subscription_id,))
            
            conn.commit()
            affected = cursor.rowcount
            conn.close()
            
        return affected > 0
    
    def get_subscription(self, subscription_id: str) -> Optional[AlertSubscription]:
        """Get a specific subscription by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM subscriptions WHERE id = ?
        ''', (subscription_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_subscription(row)
        return None
    
    def list_subscriptions(self, county_fips: str = None, 
                          state: str = None, active_only: bool = True) -> List[AlertSubscription]:
        """List all subscriptions with optional filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM subscriptions WHERE 1=1"
        params = []
        
        if county_fips:
            query += " AND county_fips = ?"
            params.append(county_fips)
        
        if state:
            query += " AND state = ?"
            params.append(state)
        
        if active_only:
            query += " AND is_active = 1"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_subscription(row) for row in rows]
    
    def trigger_alert(self, county_fips: str, alert_type: str, 
                     severity: str, message: str, 
                     data: Dict[str, Any] = None) -> List[str]:
        """
        Trigger alerts for all matching subscriptions
        
        Returns:
            List of triggered alert event IDs
        """
        import uuid
        
        if data is None:
            data = {}
        
        # Find matching active subscriptions
        subscriptions = self.list_subscriptions(county_fips=county_fips)
        triggered_events = []
        
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for sub in subscriptions:
                if alert_type not in sub.alert_types:
                    continue
                
                # Create alert event
                event_id = str(uuid.uuid4())[:8]
                event = AlertEvent(
                    id=event_id,
                    subscription_id=sub.id,
                    county_fips=county_fips,
                    alert_type=alert_type,
                    severity=severity,
                    message=message,
                    data=data,
                    triggered_at=datetime.now().isoformat(),
                    acknowledged_at=None,
                    status='active'
                )
                
                cursor.execute('''
                    INSERT INTO alert_events 
                    (id, subscription_id, county_fips, alert_type, severity,
                     message, data, triggered_at, acknowledged_at, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event.id, event.subscription_id, event.county_fips,
                    event.alert_type, event.severity, event.message,
                    json.dumps(event.data), event.triggered_at,
                    event.acknowledged_at, event.status
                ))
                
                # Update subscription's last_triggered
                cursor.execute('''
                    UPDATE subscriptions 
                    SET last_triggered = ? WHERE id = ?
                ''', (event.triggered_at, sub.id))
                
                triggered_events.append(event_id)
                
                # Send notification (mock for now)
                self._send_notification(sub, event)
            
            conn.commit()
            conn.close()
        
        return triggered_events
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Mark an alert as acknowledged"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE alert_events 
                SET status = 'acknowledged', acknowledged_at = ?
                WHERE id = ?
            ''', (datetime.now().isoformat(), alert_id))
            
            conn.commit()
            affected = cursor.rowcount
            conn.close()
            
        return affected > 0
    
    def get_active_alerts(self, county_fips: str = None,
                         alert_type: str = None) -> List[AlertEvent]:
        """Get all active (unacknowledged) alerts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM alert_events WHERE status = 'active'"
        params = []
        
        if county_fips:
            query += " AND county_fips = ?"
            params.append(county_fips)
        
        if alert_type:
            query += " AND alert_type = ?"
            params.append(alert_type)
        
        query += " ORDER BY triggered_at DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_event(row) for row in rows]
    
    def get_alert_history(self, subscription_id: str = None,
                         limit: int = 100) -> List[AlertEvent]:
        """Get alert history with optional filtering"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM alert_events WHERE 1=1"
        params = []
        
        if subscription_id:
            query += " AND subscription_id = ?"
            params.append(subscription_id)
        
        query += " ORDER BY triggered_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_event(row) for row in rows]
    
    def _send_notification(self, subscription: AlertSubscription, 
                          event: AlertEvent):
        """Send notification via configured channels (mock implementation)"""
        # TODO: Implement actual webhook, email, SMS sending
        # For hackathon, this is a mock that logs the notification
        
        notification = {
            'subscription_id': subscription.id,
            'event_id': event.id,
            'channels': [],
            'timestamp': datetime.now().isoformat()
        }
        
        if subscription.webhook_url:
            notification['channels'].append('webhook')
            # TODO: POST to webhook_url
        
        if subscription.email:
            notification['channels'].append('email')
            # TODO: Send email
        
        if subscription.phone:
            notification['channels'].append('sms')
            # TODO: Send SMS
        
        # Log notification
        print(f"[ALERT NOTIFICATION] {event.message} -> {notification['channels']}")
    
    def _row_to_subscription(self, row) -> AlertSubscription:
        """Convert database row to AlertSubscription"""
        return AlertSubscription(
            id=row[0],
            county_fips=row[1],
            county_name=row[2],
            state=row[3],
            threshold=row[4],
            alert_types=json.loads(row[5]),
            webhook_url=row[6],
            email=row[7],
            phone=row[8],
            created_at=row[9],
            last_triggered=row[10],
            is_active=bool(row[11])
        )
    
    def _row_to_event(self, row) -> AlertEvent:
        """Convert database row to AlertEvent"""
        return AlertEvent(
            id=row[0],
            subscription_id=row[1],
            county_fips=row[2],
            alert_type=row[3],
            severity=row[4],
            message=row[5],
            data=json.loads(row[6]),
            triggered_at=row[7],
            acknowledged_at=row[8],
            status=row[9]
        )


# CLI for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Alert Manager CLI")
    parser.add_argument("--subscribe", action="store_true", help="Create subscription")
    parser.add_argument("--fips", type=str, help="County FIPS code")
    parser.add_argument("--name", type=str, help="County name")
    parser.add_argument("--state", type=str, help="State abbreviation")
    parser.add_argument("--threshold", type=float, default=0.7, help="Alert threshold")
    parser.add_argument("--list", action="store_true", help="List subscriptions")
    parser.add_argument("--trigger", action="store_true", help="Trigger test alert")
    parser.add_argument("--alerts", action="store_true", help="Show active alerts")
    
    args = parser.parse_args()
    
    manager = AlertManager()
    
    if args.subscribe:
        if not all([args.fips, args.name, args.state]):
            print("Error: --fips, --name, and --state required for subscription")
            exit(1)
        
        sub_id = manager.subscribe(
            county_fips=args.fips,
            county_name=args.name,
            state=args.state,
            threshold=args.threshold
        )
        print(f"Created subscription: {sub_id}")
    
    elif args.list:
        subs = manager.list_subscriptions()
        print(f"\nActive Subscriptions ({len(subs)}):")
        for sub in subs:
            print(f"  {sub.id}: {sub.county_name}, {sub.state} (threshold: {sub.threshold})")
    
    elif args.trigger:
        if not args.fips:
            print("Error: --fips required for trigger")
            exit(1)
        
        events = manager.trigger_alert(
            county_fips=args.fips,
            alert_type="flood",
            severity="high",
            message=f"Test flood alert for county {args.fips}"
        )
        print(f"Triggered {len(events)} alerts")
    
    elif args.alerts:
        alerts = manager.get_active_alerts()
        print(f"\nActive Alerts ({len(alerts)}):")
        for alert in alerts:
            print(f"  {alert.id}: {alert.alert_type} - {alert.message}")
    
    else:
        parser.print_help()
