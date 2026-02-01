import { type ReactNode } from 'react';
import { useAuth } from '@/contexts/AuthContext';

interface SecureGateProps {
  children: ReactNode;
}

/**
 * SecureGate - Blocks rendering until user is authenticated.
 *
 * Shows loading state while verifying session.
 * Shows login prompt if not authenticated.
 * Renders children if authenticated.
 */
export function SecureGate({ children }: SecureGateProps) {
  const { isAuthenticated, loading, error, login } = useAuth();

  // Loading state
  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)',
        color: '#fafafa'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            width: 40,
            height: 40,
            border: '3px solid #333',
            borderTopColor: '#3b82f6',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 1rem'
          }} />
          <p>Verifying session...</p>
        </div>
        <style>{`
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  // Login required
  if (!isAuthenticated) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)',
        color: '#fafafa'
      }}>
        <div style={{
          textAlign: 'center',
          padding: '2rem',
          background: 'rgba(255,255,255,0.05)',
          borderRadius: '1rem',
          border: '1px solid rgba(255,255,255,0.1)'
        }}>
          <div style={{
            width: 64,
            height: 64,
            background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
            borderRadius: '1rem',
            margin: '0 auto 1.5rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '2rem'
          }}>
            🔐
          </div>
          <h1 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>
            Control Room
          </h1>
          <p style={{ color: '#888', marginBottom: '1.5rem' }}>
            Authentication required
          </p>

          {error && (
            <p style={{
              color: '#ef4444',
              marginBottom: '1rem',
              padding: '0.5rem',
              background: 'rgba(239,68,68,0.1)',
              borderRadius: '0.5rem'
            }}>
              {error}
            </p>
          )}

          <button
            onClick={login}
            style={{
              padding: '0.75rem 2rem',
              fontSize: '1rem',
              fontWeight: 500,
              color: '#fff',
              background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
              border: 'none',
              borderRadius: '0.5rem',
              cursor: 'pointer',
              transition: 'transform 0.2s, box-shadow 0.2s'
            }}
            onMouseOver={e => {
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 10px 20px rgba(59,130,246,0.3)';
            }}
            onMouseOut={e => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            Authenticate with Touch ID
          </button>

          <p style={{
            color: '#666',
            fontSize: '0.75rem',
            marginTop: '1.5rem'
          }}>
            Uses macOS Touch ID or device passcode
          </p>
        </div>
      </div>
    );
  }

  // Authenticated - render children
  return <>{children}</>;
}
