export default {
  async fetch(request, env) {
    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }

    const authHeader = request.headers.get('Authorization');
    const webhookSecret = request.headers.get('X-Webhook-Secret');
    
    // Check webhook secret if provided
    if (env.WEBHOOK_SECRET && webhookSecret !== env.WEBHOOK_SECRET) {
      return new Response('Invalid webhook secret', { status: 401 });
    }
    
    // For direct API calls, allow if no auth is required (for testing)
    // In production, you should add proper authentication
    if (!webhookSecret && !env.WEBHOOK_SECRET) {
      // Allow unauthenticated requests for now
      console.log('Warning: No authentication configured');
    }

    try {
      const data = await request.json();
      
      const timestamp = new Date().toISOString();
      const fileName = `posthog-events/${timestamp.split('T')[0]}/${timestamp.replace(/[:.]/g, '-')}-${crypto.randomUUID()}.json`;
      
      await env.POSTHOG_BUCKET.put(fileName, JSON.stringify({
        timestamp,
        headers: Object.fromEntries(request.headers.entries()),
        data
      }));

      return new Response(JSON.stringify({ success: true, fileName }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    } catch (error) {
      console.error('Error processing webhook:', error);
      return new Response(JSON.stringify({ error: 'Internal server error' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }
};