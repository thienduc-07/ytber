import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Film, User, LogOut, PlusCircle } from 'lucide-react';
import { Link } from 'react-router-dom';

interface HeaderProps {
  onNewProject?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onNewProject }) => {
  const { user, profile, signOut } = useAuth();

  return (
    <header className="sticky top-0 z-40 bg-studio-surface/80 backdrop-blur-md border-b border-studio-border px-6 py-3.5 flex items-center justify-between">
      <Link to="/" className="flex items-center gap-3 group">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-studio-primary to-studio-accent flex items-center justify-center shadow-lg group-hover:scale-105 transition">
          <Film className="w-5 h-5 text-white" />
        </div>
        <div>
          <span className="font-bold text-lg text-white tracking-tight flex items-center gap-1.5">
            AI VIDEO STUDIO <span className="text-xs bg-studio-primary/20 text-studio-primary px-2 py-0.5 rounded-full font-medium">VN</span>
          </span>
          <p className="text-xs text-gray-400 font-sans">Zero-Budget AI Shorts Platform</p>
        </div>
      </Link>

      <div className="flex items-center gap-4">
        {user ? (
          <>
            {onNewProject && (
              <button
                onClick={onNewProject}
                className="flex items-center gap-2 bg-gradient-to-r from-studio-primary to-indigo-600 hover:from-indigo-500 hover:to-indigo-700 text-white text-sm font-semibold px-4 py-2 rounded-xl shadow-md transition hover:scale-105"
              >
                <PlusCircle className="w-4 h-4" />
                Tạo Video Mới
              </button>
            )}

            <div className="flex items-center gap-3 bg-studio-card/80 border border-studio-border px-3.5 py-1.5 rounded-xl">
              <div className="w-7 h-7 rounded-full bg-studio-border flex items-center justify-center text-xs font-bold text-studio-accent">
                {profile?.full_name?.charAt(0) || user.email?.charAt(0).toUpperCase() || 'U'}
              </div>
              <div className="hidden sm:block text-left">
                <p className="text-xs font-medium text-gray-200">{profile?.full_name || user.email?.split('@')[0]}</p>
                <p className="text-[10px] text-gray-400 uppercase tracking-wider font-semibold">{profile?.tier || 'Free'}</p>
              </div>
              <button
                onClick={signOut}
                title="Đăng xuất"
                className="text-gray-400 hover:text-red-400 ml-1 p-1 transition"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </>
        ) : (
          <Link
            to="/auth"
            className="flex items-center gap-2 bg-studio-primary hover:bg-indigo-600 text-white text-sm font-medium px-4 py-2 rounded-xl transition"
          >
            <User className="w-4 h-4" />
            Đăng Nhập
          </Link>
        )}
      </div>
    </header>
  );
};
