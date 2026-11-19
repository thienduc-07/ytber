import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { Film, Lock, Mail, User as UserIcon, ArrowRight, AlertCircle, CheckCircle } from 'lucide-react';

export const AuthPage: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { signInWithEmail, signUpWithEmail } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setIsSubmitting(true);

    try {
      if (isLogin) {
        const { error } = await signInWithEmail(email, password);
        if (error) {
          setError(error.message);
        } else {
          navigate('/');
        }
      } else {
        if (!fullName.trim()) {
          setError('Vui lòng nhập họ và tên của bạn');
          setIsSubmitting(false);
          return;
        }
        const { error } = await signUpWithEmail(email, password, fullName);
        if (error) {
          setError(error.message);
        } else {
          setSuccess('Đăng ký thành công! Bạn có thể đăng nhập ngay bây giờ.');
          setIsLogin(true);
        }
      }
    } catch (err: any) {
      setError(err?.message || 'Có lỗi xảy ra, vui lòng thử lại');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-studio-bg flex flex-col justify-center items-center px-4 py-12">
      {/* Brand logo */}
      <Link to="/" className="flex items-center gap-3 mb-8 group">
        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-studio-primary to-studio-accent flex items-center justify-center shadow-xl group-hover:scale-105 transition">
          <Film className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight flex items-center gap-2">
            AI VIDEO STUDIO <span className="text-xs bg-studio-primary/20 text-studio-primary px-2.5 py-0.5 rounded-full font-bold">VN</span>
          </h1>
          <p className="text-xs text-gray-400">Nền Tảng Tạo Video Ngắn Hoàn Toàn Miễn Phí</p>
        </div>
      </Link>

      {/* Form Card */}
      <div className="w-full max-w-md bg-studio-surface border border-studio-border rounded-2xl p-8 shadow-2xl">
        <div className="text-center mb-6">
          <h2 className="text-xl font-bold text-white">
            {isLogin ? 'Đăng nhập vào Studio' : 'Tạo tài khoản mới'}
          </h2>
          <p className="text-xs text-gray-400 mt-1">
            {isLogin
              ? 'Nhập email và mật khẩu của bạn để quản lý dự án video'
              : 'Miễn phí $0 vĩnh viễn, không cần thẻ tín dụng'}
          </p>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/30 flex items-center gap-2.5 text-red-300 text-xs">
            <AlertCircle className="w-4 h-4 flex-shrink-0 text-red-400" />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="mb-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center gap-2.5 text-emerald-300 text-xs">
            <CheckCircle className="w-4 h-4 flex-shrink-0 text-emerald-400" />
            <span>{success}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-1.5">
                Họ và Tên
              </label>
              <div className="relative">
                <UserIcon className="w-4 h-4 text-gray-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Nguyễn Văn A"
                  className="w-full bg-studio-bg border border-studio-border rounded-xl pl-10 pr-3.5 py-2.5 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-studio-primary transition"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-gray-300 mb-1.5">
              Địa chỉ Email
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-gray-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="creator@example.com"
                className="w-full bg-studio-bg border border-studio-border rounded-xl pl-10 pr-3.5 py-2.5 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-studio-primary transition"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-300 mb-1.5">
              Mật Khẩu
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-gray-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="password"
                required
                minLength={6}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-studio-bg border border-studio-border rounded-xl pl-10 pr-3.5 py-2.5 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-studio-primary transition"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-3 bg-gradient-to-r from-studio-primary to-indigo-600 hover:from-indigo-500 hover:to-indigo-700 disabled:opacity-50 text-white font-bold rounded-xl shadow-lg flex items-center justify-center gap-2 transition hover:scale-[1.01] mt-2"
          >
            <span>{isLogin ? 'Đăng Nhập' : 'Tạo Tài Khoản Miễn Phí'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="mt-6 pt-4 border-t border-studio-border text-center">
          <button
            type="button"
            onClick={() => {
              setIsLogin(!isLogin);
              setError(null);
              setSuccess(null);
            }}
            className="text-xs text-gray-400 hover:text-white transition"
          >
            {isLogin ? (
              <span>Chưa có tài khoản? <strong className="text-studio-primary">Đăng ký ngay</strong></span>
            ) : (
              <span>Đã có tài khoản? <strong className="text-studio-primary">Đăng nhập</strong></span>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
