import type { Handle } from '@sveltejs/kit';

// Public routes that don't require authentication
const PUBLIC_ROUTES = ['/auth', '/health', '/api/v1/health', '/eval', '/eval.html'];

export const handle: Handle = async ({ event, resolve }) => {
	const { url, cookies } = event;
	const path = url.pathname;
	
	// Check if route is public
	const isPublicRoute = PUBLIC_ROUTES.some(route => 
		path === route || path.startsWith(route + '/')
	);
	
	// Get session token from httpOnly cookie
	const sessionToken = cookies.get('session_token');
	let isAuthenticated = false;
	
	if (sessionToken) {
		try {
			// Validate JWT token structure (must have 3 dot-separated parts)
			const parts = sessionToken.split('.');
			if (parts.length !== 3) throw new Error('Invalid JWT structure');
			const payload = JSON.parse(atob(parts[1]));
			// Check if token is expired (exp is in seconds, Date.now() is in ms)
			if (payload.exp && payload.exp > Math.floor(Date.now() / 1000)) {
				isAuthenticated = true;
				event.locals.user = {
					username: payload.username || payload.user || 'unknown',
					role: payload.role || 'user',
					authMethod: payload.authMethod || 'unknown',
					exp: payload.exp,
				};
			}
		} catch {
			// Invalid token
			cookies.delete('session_token', { path: '/' });
		}
	}
	
	// Redirect unauthenticated users to /auth
	if (!isAuthenticated && !isPublicRoute) {
		return new Response(null, {
			status: 302,
			headers: { Location: '/auth' }
		});
	}
	
	// Redirect authenticated users away from /auth
	if (isAuthenticated && path === '/auth') {
		return new Response(null, {
			status: 302,
			headers: { Location: '/' }
		});
	}
	
	const response = await resolve(event);
	return response;
};
