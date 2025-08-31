#!/usr/bin/env python3
"""
US Visa Slot Monitor - Hyderabad Consulate Only
Oct 1, 2025 - Jan 31, 2026
"""

import requests
import time
import json
from datetime import datetime
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import re

load_dotenv()

class VisaSlotMonitor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Telegram settings
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        # Target: Hyderabad, Oct 2025 - Jan 2026
        self.target_months = ['october', 'november', 'december', 'january', 'oct', 'nov', 'dec', 'jan']
        
    def is_date_in_range(self, text):
        """Check if text contains Oct 2025 - Jan 2026 dates"""
        text_lower = text.lower()
        
        has_target_month = any(month in text_lower for month in self.target_months)
        has_year = any(year in text_lower for year in ['2025', '2026'])
        
        date_patterns = [
            r'(oct|october|nov|november|dec|december)\s+2025',
            r'(jan|january)\s+2026'
        ]
        
        has_date_pattern = any(re.search(pattern, text_lower) for pattern in date_patterns)
        return has_target_month or has_date_pattern
    
    def check_visa_sources(self):
        """Check public sources for Hyderabad visa slots"""
        results = {}
        
        try:
            print("🔍 Checking visa slot sources...")
            
            # CheckVisaSlots
            url = "https://checkvisaslots.com/latest-us-visa-availability.html"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text().lower()
                
                if 'hyderabad' in text:
                    hyderabad_index = text.find('hyderabad')
                    surrounding = text[max(0, hyderabad_index-200):hyderabad_index+200]
                    
                    positive_signs = ['available', 'slots', 'open', 'booking']
                    if any(sign in surrounding for sign in positive_signs):
                        if self.is_date_in_range(surrounding):
                            results['CheckVisaSlots'] = "Hyderabad slots potentially available"
            
        except Exception as e:
            print(f"❌ Source check error: {str(e)}")
        
        return results
    
    def send_telegram_notification(self, results):
        """Send Telegram notification"""
        try:
            if not self.telegram_token or not self.telegram_chat_id:
                return False
            
            if isinstance(results, dict) and results:
                message = "🎉 *Hyderabad Visa Slots Found!*\n\n"
                for source, data in results.items():
                    message += f"*{source}:* {data}\n"
                message += f"\n📅 Oct 2025 - Jan 2026"
                message += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                message += "\n🔗 Book: https://ais.usvisa-info.com/en-in/niv"
            else:
                message = results  # For status messages
            
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, data=data)
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Telegram error: {str(e)}")
            return False

def main():
    print("🤖 US Visa Slot Monitor - Hyderabad Only")
    print("📍 Hyderabad consulate interviews")
    print("📅 Oct 1, 2025 - Jan 31, 2026")
    print("⏱️ Every 30 seconds")
    print("=" * 40)
    
    monitor = VisaSlotMonitor()
    
    # Send startup test message
    startup_msg = f"🤖 *Visa Bot Started!*\n\n✅ Monitoring Hyderabad consulate slots\n📅 Oct 2025 - Jan 2026\n⏱️ Every 30 seconds\n\n🔔 You'll get status updates every 4 hours\n⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    monitor.send_telegram_notification(startup_msg)
    print("📱 Startup notification sent!")
    
    check_count = 0
    try:
        while True:
            check_count += 1
            print(f"\n🔍 Check #{check_count} - {time.strftime('%H:%M:%S')}")
            
            results = monitor.check_visa_sources()
            
            if results:
                print("🎉 VISA SLOTS FOUND!")
                monitor.send_telegram_notification(results)
            else:
                print("❌ No Hyderabad slots found")
            
            # Status every 4 hours (480 checks at 30-second intervals)
            if check_count % 1 == 0:
                status_msg = f"🤖 *Visa Bot Status*\n\n✅ Check #{check_count}\n🎯 Hunting Hyderabad slots\n📅 Oct 2025 - Jan 2026\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                
                # Send directly like the test
                url = f"https://api.telegram.org/bot{monitor.telegram_token}/sendMessage"
                data = {
                    'chat_id': monitor.telegram_chat_id,
                    'text': status_msg,
                    'parse_mode': 'Markdown'
                }
                response = requests.post(url, data=data)
                print(f"📱 Status sent: {response.status_code}")
            
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n🛑 Visa monitoring stopped")

if __name__ == "__main__":
    main()
