const SESSION_ID_KEY = 'colbert_session_id';
const SESSION_TIMEOUT = 30 * 60 * 1000; // 30 minutes in milliseconds
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const createSession = async (): Promise<string> => {
    try {
        const response = await fetch(`${API_BASE_URL}/session/new`, {
            method: 'POST',
        });
        const data = await response.json();
        localStorage.setItem(SESSION_ID_KEY, data.session_id);
        localStorage.setItem(`${SESSION_ID_KEY}_last_activity`, Date.now().toString());
        return data.session_id;
    } catch (error) {
        console.error('Error creating session:', error);
        throw error;
    }
};

export const getSessionId = (): string | null => {
    const sessionId = localStorage.getItem(SESSION_ID_KEY);
    const lastActivity = localStorage.getItem(`${SESSION_ID_KEY}_last_activity`);
    
    if (sessionId && lastActivity) {
        const timeSinceLastActivity = Date.now() - parseInt(lastActivity);
        if (timeSinceLastActivity > SESSION_TIMEOUT) {
            // Session expired
            endSession(sessionId);
            return null;
        }
        // Update last activity
        localStorage.setItem(`${SESSION_ID_KEY}_last_activity`, Date.now().toString());
    }
    
    return sessionId;
};

export const endSession = async (sessionId: string): Promise<void> => {
    try {
        await fetch(`${API_BASE_URL}/session/${sessionId}`, {
            method: 'DELETE',
        });
        localStorage.removeItem(SESSION_ID_KEY);
        localStorage.removeItem(`${SESSION_ID_KEY}_last_activity`);
    } catch (error) {
        console.error('Error ending session:', error);
        throw error;
    }
};

export const clearSession = (): void => {
    const sessionId = localStorage.getItem(SESSION_ID_KEY);
    if (sessionId) {
        endSession(sessionId);
    }
}; 