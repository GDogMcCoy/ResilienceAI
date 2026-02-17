#!/usr/bin/env python3
"""
Release notification system for ResilienceAI
"""

import argparse
import os
from datetime import datetime
from typing import Dict, List


class ReleaseNotifier:
    def __init__(self, version: str):
        self.version = version
        self.webhook_urls = self._load_webhooks()
    
    def _load_webhooks(self) -> Dict[str, str]:
        return {
            'slack_engineering': os.getenv('SLACK_ENG_WEBHOOK'),
            'slack_releases': os.getenv('SLACK_RELEASES_WEBHOOK'),
            'pagerduty': os.getenv('PAGERDUTY_KEY'),
            'email_api': os.getenv('EMAIL_API_KEY')
        }
    
    def notify(self, channels: List[str], event_type: str = 'release'):
        for channel in channels:
            if channel == 'slack':
                self._notify_slack(event_type)
            elif channel == 'email':
                self._notify_email(event_type)
            elif channel == 'pagerduty':
                self._notify_pagerduty(event_type)
    
    def _notify_slack(self, event_type: str):
        try:
            import requests
        except ImportError:
            print("requests not installed, skipping Slack notification")
            return
        
        webhook = self.webhook_urls.get('slack_releases')
        if not webhook:
            print("Slack webhook not configured")
            return
        
        if event_type == 'release':
            message = self._get_release_message()
        elif event_type == 'rollback':
            message = self._get_rollback_message()
        else:
            message = self._get_generic_message()
        
        payload = {
            'text': message,
            'blocks': [
                {
                    'type': 'header',
                    'text': {'type': 'plain_text', 'text': f'ResilienceAI v{self.version} Released'}
                },
                {'type': 'section', 'text': {'type': 'mrkdwn', 'text': message}}
            ]
        }
        
        try:
            response = requests.post(webhook, json=payload)
            response.raise_for_status()
            print("Slack notification sent")
        except Exception as e:
            print(f"Failed to send Slack notification: {e}")
    
    def _get_release_message(self) -> str:
        return f"""
*ResilienceAI v{self.version} has been released!*

*Release Details:*
- Version: {self.version}
- Date: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}
- Environment: Production

*What's New:*
See the full release notes: https://github.com/resilienceai/platform/releases/tag/v{self.version}

*Deployment Status:*
All services have been successfully deployed and are operational.

*Need Help?*
Contact #resilienceai-support or email support@resilienceai.io
"""
    
    def _get_rollback_message(self) -> str:
        return f"""
*Rollback Executed for ResilienceAI v{self.version}*

*Rollback Details:*
- Version: {self.version}
- Date: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}
- Environment: Production

*Status:*
Rollback completed successfully. All services are operational.

*Next Steps:*
Engineering team is investigating the root cause.
"""
    
    def _get_generic_message(self) -> str:
        return f"ResilienceAI v{self.version} - {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}"
    
    def _notify_email(self, event_type: str):
        print(f"Email notification for {event_type} would be sent here")
    
    def _notify_pagerduty(self, event_type: str):
        print(f"PagerDuty notification for {event_type} would be sent here")


def main():
    parser = argparse.ArgumentParser(description='Send release notifications')
    parser.add_argument('--version', required=True, help='Release version')
    parser.add_argument('--channels', default='slack', help='Comma-separated list of channels')
    parser.add_argument('--event', default='release', choices=['release', 'rollback', 'announcement'])
    args = parser.parse_args()
    
    notifier = ReleaseNotifier(args.version)
    channels = [c.strip() for c in args.channels.split(',')]
    notifier.notify(channels, args.event)


if __name__ == '__main__':
    main()
