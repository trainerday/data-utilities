// TrainerDay Event Tracker - Direct to Cloudflare R2
class TrainerDayTracker {
  constructor(config = {}) {
    this.endpoint = config.endpoint || 'https://posthog-to-r2.av-958.workers.dev';
    this.webhookSecret = config.webhookSecret || 'cfb92e462c727f6487149c3a7c0337dc24787e904fd438da54fcf665d613f8bd';
    this.userId = null;
    this.sessionId = this.generateSessionId();
    this.deviceId = this.getOrCreateDeviceId();
    
    // Auto-capture page views
    if (config.capturePageview !== false) {
      this.capturePageview();
    }
  }
  
  generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  
  getOrCreateDeviceId() {
    let deviceId = localStorage.getItem('td_device_id');
    if (!deviceId) {
      deviceId = `device_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('td_device_id', deviceId);
    }
    return deviceId;
  }
  
  identify(userId, properties = {}) {
    this.userId = userId;
    this.capture('identify', {
      ...properties,
      $user_id: userId
    });
  }
  
  capture(event, properties = {}) {
    const enrichedData = {
      event,
      properties: {
        ...this.getAutoProperties(),
        ...properties,
        time: Date.now(),
        timestamp: new Date().toISOString()
      },
      distinct_id: this.userId || this.deviceId,
      session_id: this.sessionId
    };
    
    // Send to worker
    fetch(this.endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Webhook-Secret': this.webhookSecret
      },
      body: JSON.stringify(enrichedData)
    }).then(response => {
      if (!response.ok) {
        console.error('Failed to send event:', response.status);
      }
    }).catch(error => {
      console.error('Error sending event:', error);
    });
    
    // Log in console for debugging
    if (window.tdDebug) {
      console.log('TrainerDay Event:', enrichedData);
    }
  }
  
  capturePageview() {
    this.capture('pageview', {
      $current_url: window.location.href,
      $host: window.location.hostname,
      $pathname: window.location.pathname,
      $referrer: document.referrer,
      title: document.title
    });
  }
  
  getAutoProperties() {
    return {
      $device_id: this.deviceId,
      $session_id: this.sessionId,
      $current_url: window.location.href,
      $host: window.location.hostname,
      $pathname: window.location.pathname,
      $screen_height: window.screen.height,
      $screen_width: window.screen.width,
      $viewport_height: window.innerHeight,
      $viewport_width: window.innerWidth,
      $lib: 'trainerday-tracker',
      $lib_version: '1.0.0',
      $browser: this.getBrowser(),
      $browser_language: navigator.language,
      $os: this.getOS(),
      $device_type: this.getDeviceType(),
      $user_agent: navigator.userAgent
    };
  }
  
  getBrowser() {
    const ua = navigator.userAgent;
    if (ua.indexOf('Chrome') > -1) return 'Chrome';
    if (ua.indexOf('Safari') > -1) return 'Safari';
    if (ua.indexOf('Firefox') > -1) return 'Firefox';
    if (ua.indexOf('Edge') > -1) return 'Edge';
    return 'Unknown';
  }
  
  getOS() {
    const ua = navigator.userAgent;
    if (ua.indexOf('Windows') > -1) return 'Windows';
    if (ua.indexOf('Mac') > -1) return 'MacOS';
    if (ua.indexOf('Linux') > -1) return 'Linux';
    if (ua.indexOf('Android') > -1) return 'Android';
    if (ua.indexOf('iOS') > -1) return 'iOS';
    return 'Unknown';
  }
  
  getDeviceType() {
    const ua = navigator.userAgent;
    if (/tablet|ipad|playbook|silk/i.test(ua)) return 'tablet';
    if (/mobile|iphone|ipod|android|blackberry|opera|mini|windows\sce|palm|smartphone|iemobile/i.test(ua)) return 'mobile';
    return 'desktop';
  }
}

// Export for use
window.TrainerDayTracker = TrainerDayTracker;