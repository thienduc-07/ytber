import React, { useState, useEffect } from 'react';
import { Header } from '../components/layout/Header';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import type { Project, GenreInfo } from '../types/database';
import { apiClient } from '../services/apiClient';
import { 
  PlusCircle, Sparkles, Clock, FolderOpen, Trash2, ArrowRight, Zap, Film
} from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newVideoType, setNewVideoType] = useState<'short-form' | 'long-form'>('short-form');
  const [newGenre, setNewGenre] = useState('general');
  const [showNewModal, setShowNewModal] = useState(false);
  const [genres, setGenres] = useState<GenreInfo[]>([]);

  useEffect(() => {
    loadProjects();
    apiClient.fetchGenres().then(setGenres).catch(console.warn);
  }, [user]);

  const loadProjects = async () => {
    setLoading(true);
    try {
      const projs = await apiClient.listProjects();
      setProjects(projs);
    } catch (e) {
      console.warn('API listProjects failed, using local storage fallback:', e);
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
            video_type: 'short-form',
            genre: 'historical_doc',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          }
        ];
        setProjects(demo);
        localStorage.setItem('demo_projects', JSON.stringify(demo));
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async (titleToCreate?: string, type?: 'short-form' | 'long-form', g?: string) => {
    const title = titleToCreate || newTitle || 'Dự Án Video AI';
    const vType = type || newVideoType;
    const vGenre = g || newGenre;
    setIsCreating(true);

    try {
      const created = await apiClient.createProject({
        title: title,
        description: `Dự án ${vType === 'long-form' ? 'video ngang dài' : 'video ngắn dọc'} thể loại ${vGenre}`,
        video_type: vType,
        genre: vGenre,
      });

      setShowNewModal(false);
      setNewTitle('');
      navigate(`/studio/${created.id}`);
    } catch (e) {
      console.warn('API createProject failed, using local storage fallback:', e);
      const newProj: Project = {
        id: `demo-${Date.now()}`,
        user_id: 'anonymous',
        title: title,
        description: 'Dự án tạo trong phiên thử nghiệm',
        status: 'draft',
        video_type: vType,
        genre: vGenre,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      const updated = [newProj, ...projects];
      setProjects(updated);
      localStorage.setItem('demo_projects', JSON.stringify(updated));
      setShowNewModal(false);
      setNewTitle('');
      navigate(`/studio/${newProj.id}`);
    } finally {
      setIsCreating(false);
    }
  };

  const handleDeleteProject = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Bạn có chắc chắn muốn xóa dự án này?')) return;

    try {
      await apiClient.deleteProject(id);
    } catch (err) {
      console.warn('API delete failed, updating local state:', err);
    }

    const updated = projects.filter((p) => p.id !== id);
    setProjects(updated);
    localStorage.setItem('demo_projects', JSON.stringify(updated));
  };

  return (
    <div className="min-h-screen bg-studio-bg flex flex-col">
      <Header />

      <main className="flex-1 max-w-7xl w-full mx-auto p-6 md:p-8 flex flex-col gap-8">
        {/* Hero Banner */}
        <section className="bg-gradient-to-r from-studio-surface via-studio-card to-studio-surface border border-studio-border rounded-3xl p-6 md:p-8 shadow-2xl relative overflow-hidden flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="space-y-3 max-w-xl z-10">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-studio-primary/20 border border-studio-primary/40 text-studio-primary text-xs font-semibold">
              <Zap className="w-3.5 h-3.5" />
              <span>Nền Tảng Sản Xuất Video AI Tích Hợp Đa Thể Loại</span>
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight leading-tight">
              Sản Xuất Video Shorts & Long-Form Hoàn Toàn Tự Động
            </h1>
            <p className="text-sm text-gray-300 leading-relaxed">
              Nhập kịch bản tiếng Việt bất kỳ. Hệ thống tự động phân tích thể loại (Genre Intelligence), nghiên cứu tư liệu bản quyền mở, tạo giọng đọc Neural Edge-TTS và kết xuất video MP4 trực tiếp.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-3 z-10 w-full md:w-auto">
            <button
              onClick={() => {
                setNewVideoType('short-form');
                setShowNewModal(true);
              }}
              className="px-5 py-3 bg-gradient-to-r from-studio-primary to-indigo-600 hover:from-indigo-500 hover:to-indigo-700 text-white font-bold rounded-2xl shadow-lg flex items-center justify-center gap-2 transition hover:scale-105"
            >
              <PlusCircle className="w-5 h-5" />
              <span>Tạo Video Shorts (9:16)</span>
            </button>
            <button
              onClick={() => {
                setNewVideoType('long-form');
                setShowNewModal(true);
              }}
              className="px-5 py-3 bg-studio-card hover:bg-studio-border border border-studio-border text-gray-200 font-bold rounded-2xl shadow-lg flex items-center justify-center gap-2 transition hover:scale-105"
            >
              <Film className="w-5 h-5 text-studio-accent" />
              <span>Tạo Long-Form (16:9)</span>
            </button>
          </div>
        </section>

        {/* Projects Grid Section */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <FolderOpen className="w-5 h-5 text-studio-primary" />
              Dự Án Đã Tạo ({projects.length})
            </h2>
          </div>

          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {[1, 2, 3].map((i) => (
                <div key={i} className="bg-studio-surface border border-studio-border rounded-2xl p-5 h-44 animate-pulse" />
              ))}
            </div>
          ) : projects.length === 0 ? (
            <div className="bg-studio-surface border border-studio-border border-dashed rounded-2xl p-12 text-center flex flex-col items-center gap-3">
              <div className="w-12 h-12 rounded-2xl bg-studio-primary/20 flex items-center justify-center text-studio-primary">
                <Sparkles className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-white">Chưa Có Dự Án Nào</h3>
              <p className="text-xs text-gray-400 max-w-sm">
                Hãy bắt đầu tạo video đầu tiên bằng cách dán kịch bản hoặc chọn một kịch bản mẫu bên dưới.
              </p>
              <button
                onClick={() => setShowNewModal(true)}
                className="mt-2 px-4 py-2 bg-studio-primary hover:bg-indigo-600 text-white text-xs font-bold rounded-xl transition"
              >
                Tạo Dự Án Ngay
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {projects.map((proj) => (
                <div
                  key={proj.id}
                  onClick={() => navigate(`/studio/${proj.id}`)}
                  className="group bg-studio-surface hover:bg-studio-card border border-studio-border hover:border-studio-primary/50 rounded-2xl p-5 shadow-lg transition-all cursor-pointer flex flex-col justify-between hover:shadow-2xl hover:-translate-y-0.5"
                >
                  <div className="space-y-2.5">
                    <div className="flex items-start justify-between gap-2">
                      <h3 className="text-sm font-bold text-white group-hover:text-studio-highlight transition line-clamp-1">
                        {proj.title}
                      </h3>
                      <button
                        onClick={(e) => handleDeleteProject(proj.id, e)}
                        className="text-gray-500 hover:text-red-400 transition p-1"
                        title="Xóa dự án"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>

                    <p className="text-xs text-gray-400 line-clamp-2 leading-relaxed">
                      {proj.description || 'Chưa có mô tả chi tiết cho dự án này.'}
                    </p>

                    <div className="flex items-center gap-2 pt-1">
                      <span className="text-[10px] bg-studio-primary/20 text-studio-primary border border-studio-primary/30 px-2 py-0.5 rounded-full font-mono uppercase">
                        {proj.video_type || 'short-form'}
                      </span>
                      {proj.genre && (
                        <span className="text-[10px] bg-studio-accent/20 text-studio-accent border border-studio-accent/30 px-2 py-0.5 rounded-full font-mono">
                          {proj.genre}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-4 mt-2 border-t border-studio-border/50 text-[11px] text-gray-500">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5" />
                      {new Date(proj.updated_at).toLocaleDateString('vi-VN')}
                    </span>

                    <span className="flex items-center gap-1 font-semibold text-studio-primary group-hover:translate-x-1 transition">
                      Mở Studio <ArrowRight className="w-3.5 h-3.5" />
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Quick Start Templates */}
        <section className="bg-studio-surface border border-studio-border rounded-2xl p-6 shadow-xl space-y-4">
          <h2 className="text-sm font-bold text-white flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-studio-accent" />
            Khởi Động Nhanh Với Thể Loại Định Hình Sẵn
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { title: 'Chiến Thắng Điện Biên Phủ 1954', genre: 'historical_doc', type: 'short-form', tag: 'Lịch Sử / 9:16' },
              { title: 'Bí Ẩn Căn Nhà Ma Cuối Làng', genre: 'horror', type: 'short-form', tag: 'Kinh Dị / 9:16' },
              { title: 'Tăng Trưởng Kinh Tế Việt Nam 2024', genre: 'economics', type: 'long-form', tag: 'Kinh Tế / 16:9' },
              { title: 'Nguyên Lý Cộng Hưởng Cầu Broughton', genre: 'science', type: 'short-form', tag: 'Khoa Học / 9:16' },
            ].map((template, idx) => (
              <button
                key={idx}
                onClick={() => handleCreateProject(template.title, template.type as any, template.genre)}
                className="bg-studio-card/60 hover:bg-studio-card border border-studio-border hover:border-gray-500 rounded-xl p-3.5 text-left transition flex flex-col justify-between"
              >
                <p className="text-xs font-semibold text-white line-clamp-1">{template.title}</p>
                <span className="text-[10px] text-studio-accent mt-2 font-medium">{template.tag}</span>
              </button>
            ))}
          </div>
        </section>
      </main>

      {/* New Project Modal */}
      {showNewModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="bg-studio-surface border border-studio-border rounded-2xl max-w-md w-full p-6 shadow-2xl flex flex-col gap-4">
            <h3 className="text-base font-bold text-white">Tạo Dự Án Video Mới</h3>
            
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
                placeholder="Ví dụ: Chiến thắng Điện Biên Phủ 1954..."
                className="w-full bg-studio-bg border border-studio-border rounded-xl px-3.5 py-2.5 text-xs text-gray-100 placeholder-gray-500 focus:outline-none focus:border-studio-primary transition"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1.5">
                  Định Dạng Video
                </label>
                <select
                  value={newVideoType}
                  onChange={(e) => setNewVideoType(e.target.value as any)}
                  className="w-full bg-studio-bg border border-studio-border rounded-xl px-3 py-2 text-xs text-gray-200 focus:outline-none focus:border-studio-primary"
                >
                  <option value="short-form">Shorts / TikTok (9:16)</option>
                  <option value="long-form">Long-form (16:9)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1.5">
                  Thể Loại
                </label>
                <select
                  value={newGenre}
                  onChange={(e) => setNewGenre(e.target.value)}
                  className="w-full bg-studio-bg border border-studio-border rounded-xl px-3 py-2 text-xs text-gray-200 focus:outline-none focus:border-studio-primary"
                >
                  {genres.map(g => (
                    <option key={g.genre_id} value={g.genre_id}>{g.display_name.split(' (')[0]}</option>
                  ))}
                </select>
              </div>
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
                {isCreating ? 'Đang tạo...' : 'Bắt Đầu Dự Án'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
