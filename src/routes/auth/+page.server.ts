import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ cookies, url }) => {
	// Check if user is already authenticated
	const sessionToken = cookies.get('session_token');
	
	if (sessionToken) {
		try {
			const payload = JSON.parse(atob(sessionToken.split('.')[1]));
			if (payload.exp && payload.exp > Date.now()) {
				// Already authenticated, redirect to dashboard
				return {
					status: 302,
					headers: { Location: '/' }
				};
			}
		} catch {
			// Invalid token, will show login page
		}
	}
	
	return {
		isAuthenticated: false
	};
};
