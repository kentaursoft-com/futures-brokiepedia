import { redirect, type Handle } from '@sveltejs/kit';

const PUBLIC_ROUTES = ['/auth', '/health', '/api/v1/health', '/eval'];

export const handle: Handle = async ({ event, resolve }) => {
	const { url, cookies } = event;
	const path = url.pathname;
	
	const isPublicRoute = PUBLIC_ROUTES.some(route => 
		path === route || path.startsWith(route + '/')
	);
	
	const sessionToken = cookies.get('session_token');
	let isAuthenticated = false;
	
	if (sessionToken) {
		try {
			const parts = sessionToken.split('.');
			if (parts.length !== 3) throw new Error('Invalid JWT structure');
			const payload = JSON.parse(atob(parts[1]));
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
			cookies.delete('session_token', { path: '/' });
		}
	}
	
	if (!isAuthenticated && !isPublicRoute) {
		throw redirect(302, '/auth');
	}
	
	if (isAuthenticated && path === '/auth') {
		throw redirect(302, '/');
	}
	
	const response = await resolve(event);
	return response;
};
