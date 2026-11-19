import React, { useState, useEffect } from 'react';
import { Header } from '../components/layout/Header';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import type { Project } from '../types/database';
import { supabase } from '../services/supabase';
import { 
  PlusCircle, Sparkles, Clock, FolderOpen, Trash2, ArrowRight, Zap, ShieldCheck
} from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { user, profile } = useAuth();
  const navigate = useNavigate();

  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [showNewModal, setShowNewModal] = useState(false);

  useEffect(() => {
    loadProjects();
  }, [user]);

  const loadProjects = async () => {
    setLoading(true);
    if (!user) {
      // Local demo mode for unauthenticated users
      const local = localStorage.getItem('demo_projects');
      if (local) {
        setProjects(JSON.parse(local));
      } else {
        const demo: Project[] = [
          {
            id: 'demo-p1',
            user_id: 'anonymous',
            title: 'Chiến Thắng Điện Biên Phủ 1954',
            description: 'Kịch bản lịch sử hào hùng 60s cho Shorts/TikTok',
            status: 'ready',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          }
        ];
        setProjects(demo);
        localStorage.setItem('demo_projects', JSON.stringify(demo));
      }
      setLoading(false);
      return;
    }

    try {
      const { data, error } = await supabase
        .from('projects')
        .select('*')
        .order('updated_at', { ascending: false });

      if (!error && data) {
        setProjects(data as Project[]);
      }
    } catch (e) {
      console.error('Error fetching projects:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async (titleToCreate?: string) => {
    const title = titleToCreate || newTitle || 'Video Ngắn Không Tiêu Đề';
    setIsCreating(true);

    try {
      if (!user) {
        const newProj: Project = {
          id: `demo-${Date.now()}`,
          user_id: 'anonymous',
          title: title,
          description: 'Dự án tạo trong phiên thử nghiệm',
          status: 'draft',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };
        const updated = [newProj, ...projects];
        setProjects(updated);
        localStorage.setItem('demo_projects', JSON.stringify(updated));
        setShowNewModal(false);
        setNewTitle('');
        navigate(`/studio/${newProj.id}`);
        return;
      }

      const { data, error } = await supabase
        .from('projects')
        .insert({
          user_id: user.id,
          title: title,
          status: 'draft',
        })
        .select()
        .single();

      if (!error && data) {
        setShowNewModal(false);
        setNewTitle('');
        navigate(`/studio/${data.id}`);
      }
    } catch (e) {
      console.error('Error creating project:', e);
    } finally {
      setIsCreating(false);
    }
  };

  const handleDeleteProject = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Bạn có chắc chắn muốn xóa dự án này?')) return;

    if (!user) {
      const updated = projects.filter((p) => p.id !== id);
      setProjects(updated);
      localStorage.setItem('demo_projects', JSON.stringify(updated));
      return;
    }

    await supabase.from('projects').delete().eq('id', id);
    setProjects(projects.filter((p) => p.id !== id));
  };

  return (
    <div className="min-h-screen bg-studio-bg flex flex-col">
      <Header onNewProject={() => setShowNewModal(true)} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8 flex flex-col gap-8">
        {/* Welcome & Quota Hero Banner */}
        <section className="bg-gradient-to-r from-studio-surface via-studio-card to-studio-surface border border-studio-border rounded-3xl p-8 relative overflow-hidden shadow-2xl">
          <div className="absolute right-0 top-0 w-96 h-96 bg-studio-primary/10 rounded-full blur-3xl pointer-events-none" />
          <div className="relative z-10 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
            <div className="max-w-2xl">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-studio-primary/20 border border-studio-primary/30 text-studio-primary text-xs font-bold mb-3">
                <Sparkles className="w-3.5 h-3.5" />
                <span>NỀN TẢNG AI SHORTS KHÔNG TỐN CHI PHÍ (ZERO-BUDGET)</span>
              </div>
              <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight leading-tight">
                Sản Xuất Video Ngắn Tiếng Việt Tự Động 100% Trong Trình Duyệt
              </h1>
              <p className="text-gray-400 text-sm mt-3 leading-relaxed">
                Tự động hóa toàn bộ quy trình: Nhập kịch bản tiếng Việt → Phân tích cảnh → Khám phá tư liệu mở CC0/Wikimedia → Tạo phụ đề động → Kết xuất H.264 1080×1920 30FPS bằng WebCodecs trực tiếp trên máy của bạn mà không tốn máy chủ.
              </p>
            </div>

            {/* Quota overview */}
            <div className="bg-studio-bg/80 border border-studio-border rounded-2xl p-4 w-full lg:w-72 flex flex-col gap-3">
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-400">Gói tài khoản:</span>
                <span className="font-bold text-studio-accent uppercase">{profile?.tier || 'Free $0.00'}</span>
              </div>
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-gray-300">Phân tích kịch bản hôm nay</span>
                  <span className="font-mono text-white font-semibold">1 / 20</span>
                </div>
                <div className="w-full bg-studio-surface h-1.5 rounded-full overflow-hidden">
                  <div className="bg-studio-primary h-full w-[5%]" />
                </div>
              </div>
              <div className="flex items-center gap-1.5 text-[11px] text-emerald-400">
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>Hạ tầng không tốn phí bản quyền</span>
              </div>
            </div>
          </div>
        </section>

        {/* Project Section */}
        <section className="flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FolderOpen className="w-5 h-5 text-studio-primary" />
              <h2 className="text-xl font-bold text-white">Dự Án Của Bạn</h2>
              <span className="text-xs bg-studio-card text-gray-400 px-2.5 py-0.5 rounded-full border border-studio-border">
                {projects.length} dự án
              </span>
            </div>

            <button
              onClick={() => setShowNewModal(true)}
              className="flex items-center gap-2 bg-studio-primary hover:bg-indigo-600 text-white text-xs font-bold px-3.5 py-2 rounded-xl transition shadow"
            >
              <PlusCircle className="w-4 h-4" />
              Tạo Dự Án Mới
            </button>
          </div>

          {/* Projects Grid */}
          {loading ? (
            <div className="py-12 flex justify-center text-sm text-gray-400">
              Đang tải danh sách dự án...
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {/* New Project Quick Trigger */}
              <div
                onClick={() => setShowNewModal(true)}
                className="border-2 border-dashed border-studio-border hover:border-studio-primary rounded-2xl p-6 flex flex-col items-center justify-center text-center cursor-pointer group bg-studio-surface/40 hover:bg-studio-surface/70 transition min-h-[190px]"
              >
                <div className="w-12 h-12 rounded-2xl bg-studio-card group-hover:bg-studio-primary/20 flex items-center justify-center text-gray-400 group-hover:text-studio-primary transition mb-3">
                  <PlusCircle className="w-6 h-6" />
                </div>
                <h3 className="font-bold text-white text-sm group-hover:text-studio-primary transition">
                  Tạo Video Ngắn Mới
                </h3>
                <p className="text-xs text-gray-500 mt-1 max-w-xs">
                  Nhập kịch bản tiếng Việt hoặc chọn kịch bản mẫu có sẵn
                </p>
              </div>

              {/* Existing Projects */}
              {projects.map((proj) => (
                <div
                  key={proj.id}
                  onClick={() => navigate(`/studio/${proj.id}`)}
                  className="bg-studio-surface hover:bg-studio-card/80 border border-studio-border hover:border-studio-primary/60 rounded-2xl p-5 flex flex-col justify-between transition cursor-pointer group shadow-lg min-h-[190px]"
                >
                  <div>
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md bg-studio-border text-gray-300">
                        {proj.status}
                      </span>
                      <button
                        onClick={(e) => handleDeleteProject(proj.id, e)}
                        className="text-gray-500 hover:text-red-400 p-1 transition"
                        title="Xóa dự án"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>

                    <h3 className="font-bold text-white text-base group-hover:text-studio-accent transition line-clamp-2">
                      {proj.title}
                    </h3>
                    <p className="text-xs text-gray-400 mt-1.5 line-clamp-2">
                      {proj.description || 'Chưa có mô tả chi tiết'}
                    </p>
                  </div>

                  <div className="pt-4 border-t border-studio-border flex items-center justify-between text-xs text-gray-500">
                    <div className="flex items-center gap-1.5">
                      <Clock className="w-3.5 h-3.5" />
                      <span>{new Date(proj.updated_at).toLocaleDateString('vi-VN')}</span>
                    </div>
                    <span className="text-studio-primary group-hover:translate-x-1 transition font-semibold flex items-center gap-1">
                      Mở Studio <ArrowRight className="w-3.5 h-3.5" />
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Quick Starter Templates */}
          <div className="mt-6 pt-6 border-t border-studio-border">
            <h3 className="text-sm font-bold text-gray-300 mb-3 flex items-center gap-2">
              <Zap className="w-4 h-4 text-studio-highlight" />
              Mẫu Kịch Bản Khởi Tạo Nhanh (1 Click)
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {[
                {
                  title: 'Hồ Gươm & Truyền Thuyết Rùa Vàng',
                  tag: 'Lịch Sử / Văn Hóa',
                },
                {
                  title: 'Bí Ẩn Về Hố Đen Vũ Trụ',
                  tag: 'Khoa Học / Vũ Trụ',
                },
                {
                  title: '5 Bí Mật Chưa Từng Kể Về Cà Phê Trứng',
                  tag: 'Ẩm Thực / Du Lịch',
                },
              ].map((template, idx) => (
                <button
                  key={idx}
                  onClick={() => handleCreateProject(template.title)}
                  className="bg-studio-card/60 hover:bg-studio-card border border-studio-border hover:border-gray-500 rounded-xl p-3.5 text-left transition flex flex-col justify-between"
                >
                  <p className="text-xs font-semibold text-white">{template.title}</p>
                  <span className="text-[10px] text-studio-accent mt-2 font-medium">{template.tag}</span>
                </button>
              ))}
            </div>
          </div>
        </section>
      </main>

      {/* New Project Modal */}
      {showNewModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="bg-studio-surface border border-studio-border rounded-2xl max-w-md w-full p-6 shadow-2xl flex flex-col gap-4">
            <h3 className="text-lg font-bold text-white">Tạo Dự Án Video Mới</h3>
            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-1.5">
                Tên Dự Án / Chủ Đề Video
              </label>
              <input
                type="text"
                autoFocus
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleCreateProject()}
                placeholder="Ví dụ: Lịch sử áo dài Việt Nam qua các thời kỳ..."
                className="w-full bg-studio-bg border border-studio-border rounded-xl px-3.5 py-2.5 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-studio-primary transition"
              />
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <button
                onClick={() => setShowNewModal(false)}
                className="px-4 py-2 text-xs font-semibold text-gray-400 hover:text-white transition"
              >
                Hủy
              </button>
              <button
                onClick={() => handleCreateProject()}
                disabled={isCreating}
                className="px-4 py-2 bg-studio-primary hover:bg-indigo-600 disabled:opacity-50 text-white text-xs font-bold rounded-xl shadow transition"
              >
                {isCreating ? 'Đang tạo...' : 'Tạo Dự Án'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
