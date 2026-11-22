import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { RemotionPlayer } from '../components/video/RemotionPlayer';
import { StoryboardEditor } from '../components/storyboard/StoryboardEditor';
import { TimelineEditor } from '../components/storyboard/TimelineEditor';
import { RenderModal } from '../components/video/RenderModal';
import { apiClient, getAuthHeaders } from '../services/apiClient';
import type { SceneManifest, SceneItem, Project, GenreInfo, VoiceInfo } from '../types/database';
import { 
  Sparkles, Play, ArrowLeft, Save, Sliders, Volume2, Mic, Film, Check, BookOpen, Layers, Music, Headphones, Image as ImageIcon,
  Search, ExternalLink, ChevronDown, ChevronUp
} from 'lucide-react';

const buildDefaultManifestForProject = (
  title: string,
  genre: string,
  videoType: 'short-form' | 'long-form',
  episodeId: string
): { manifest: SceneManifest; script: string; topic: string } => {
  const isLong = videoType === 'long-form';
  const width = isLong ? 1920 : 1080;
  const height = isLong ? 1080 : 1920;
  const aspect_ratio = isLong ? '16:9' : '9:16';

  const g = (genre || '').toLowerCase();
  const t = (title || '').toLowerCase();

  if (g.includes('horror') || t.includes('ma') || t.includes('kinh dị') || t.includes('căn nhà')) {
    const script = `🎬 CĂN NHÀ GỖ CUỐI LÀNG

Thể loại: Kinh dị tâm linh – Bí ẩn – Psychological Horror
Thời lượng dự kiến: 3–4 phút
Phong cách hình ảnh: Cinematic 3D Animation, Gothic Horror, Dark Fantasy, Vietnamese Folklore.
Bối cảnh: Một ngôi làng Việt Nam cổ kính vào những năm 1970, sương mù dày đặc, ánh trăng lạnh, những căn nhà gỗ cũ kỹ.

⸻

KỊCH BẢN CHI TIẾT – 16 PHÂN CẢNH

PHÂN CẢNH 1 – LỜI CẢNH BÁO
Hình ảnh: Góc máy flycam lướt qua một ngôi làng hẻo lánh giữa màn đêm. Những mái nhà phủ rêu, con đường đất quanh co, ánh trăng mờ ảo. Cuối con đường là một căn nhà gỗ lớn, đứng cô độc giữa màn sương.
Camera: Slow cinematic aerial push-in.
Lời dẫn: “Bạn có dám bước chân vào căn nhà gỗ cổ kính ở cuối làng, nơi mà ngay cả những người gan dạ nhất cũng không dám đi ngang qua sau khi trời tối?”

PHÂN CẢNH 2 – NGÔI NHÀ BỊ LÃNG QUÊN
Hình ảnh: Cận cảnh căn nhà gỗ mục nát. Mái ngói sụp xuống, những cánh cửa rung lên dù không có gió. Một chiếc xích đu cũ kỹ trước sân tự chuyển động.
Camera: Slow tracking shot từ cổng vào nhà.
Lời dẫn: “Người dân kể rằng, căn nhà ấy đã bị bỏ hoang gần năm mươi năm. Không ai biết chủ nhân cuối cùng của nó là ai. Nhưng có một điều tất cả đều biết…”

PHÂN CẢNH 3 – NGỌN ĐÈN LÚC NỬA ĐÊM
Hình ảnh: Đồng hồ quả lắc trong căn nhà cổ. Kim phút từ từ tiến đến số 12. Tiếng tích tắc ngày càng lớn. Đúng 00:00, ngọn đèn dầu trên bàn thờ đột nhiên bùng cháy.
Camera: Extreme close-up đồng hồ → whip pan sang ngọn đèn.
Lời dẫn: “Cứ đúng mười hai giờ đêm, ngọn đèn dầu trên bàn thờ lại tự động bốc cháy. Dù không có ai châm lửa. Dù căn nhà đã không còn điện hay người ở từ hàng chục năm trước.”

PHÂN CẢNH 4 – TIẾNG BƯỚC CHÂN
Hình ảnh: Hành lang tối om. Một vệt bóng đen thấp thoáng cuối hành lang. Sàn gỗ phát ra tiếng kẽo kẹt. Từng dấu chân ướt xuất hiện trên sàn, mặc dù không có ai.
Camera: Low-angle tracking shot sát mặt sàn.
Âm thanh: Tiếng gỗ cót két, tiếng bước chân chậm rãi, tiếng gió rít.
Lời dẫn: “Nhưng điều đáng sợ nhất không phải ngọn đèn. Mà là tiếng bước chân. Đêm nào cũng vậy, cứ sau khi ngọn đèn sáng lên, lại có ai đó đi lại trong căn nhà.”

PHÂN CẢNH 5 – NGƯỜI KHÁCH KHÔNG MỜI
Hình ảnh: Một chàng trai trẻ tên Minh đứng trước cổng nhà, tay cầm đèn pin và chiếc máy quay cũ. Anh quyết định bước vào để tìm hiểu sự thật.
Camera: Medium shot từ phía sau nhân vật, ánh đèn pin xuyên qua màn sương.
Lời dẫn: “Một đêm nọ, Minh – chàng trai trẻ vừa trở về làng – quyết định tự mình khám phá bí mật ấy. Anh mang theo máy quay, đèn pin và một chiếc điện thoại. Anh tin rằng mọi câu chuyện ma quỷ đều có lời giải thích.”

PHÂN CẢNH 6 – CÁNH CỬA TỰ MỞ
Hình ảnh: Minh chạm tay vào cánh cửa gỗ. Cánh cửa từ từ mở ra với tiếng rít dài. Bên trong là một căn phòng phủ đầy bụi. Những bức ảnh gia đình cũ treo nghiêng trên tường.
Camera: Over-the-shoulder shot, từ sau lưng Minh nhìn vào căn phòng.
Lời dẫn: “Nhưng ngay khi anh vừa chạm vào cánh cửa, nó đã tự mở ra. Bên trong, mọi thứ vẫn được giữ nguyên như thể chủ nhân căn nhà chỉ vừa rời đi vài phút trước.”

PHÂN CẢNH 7 – BỨC ẢNH KỲ LẠ
Hình ảnh: Minh soi đèn pin vào một bức ảnh gia đình cũ. Trong ảnh có một người đàn ông, một người phụ nữ và một bé gái. Gương mặt bé gái bị cào xước gần như không thể nhận ra.
Camera: Extreme close-up vào bức ảnh, sau đó chuyển nét sang gương mặt Minh.
Lời dẫn: “Trên tường là bức ảnh của một gia đình ba người. Nhưng kỳ lạ thay, khuôn mặt cô bé trong ảnh đã bị ai đó cố tình cào nát.”

PHÂN CẢNH 8 – TIẾNG THÌ THẦM
Hình ảnh: Minh quay đầu về phía cầu thang. Một giọng nữ thì thầm vang lên ngay sau gáy. Ánh đèn pin chập chờn rồi tắt phụt.
Camera: Close-up khuôn mặt Minh, camera từ từ xoay về phía bóng tối sau lưng.
Lời dẫn: “Bỗng nhiên, một giọng nói rất nhỏ vang lên ngay sau lưng anh… Minh… cuối cùng anh cũng về rồi…”

PHÂN CẢNH 9 – CĂN PHÒNG KHÓA KÍN
Hình ảnh: Minh phát hiện một cánh cửa nhỏ dưới gầm cầu thang. Trên cửa có những vết cào sâu từ bên trong. Một chiếc ổ khóa gỉ sét nằm trên nền nhà.
Camera: Slow dolly-in vào cánh cửa.
Lời dẫn: “Anh lần theo âm thanh và phát hiện một căn phòng nhỏ bị khóa kín dưới gầm cầu thang. Trên cánh cửa là hàng chục vết cào sâu. Điều đáng sợ là… tất cả đều hướng từ bên trong ra ngoài.”

PHÂN CẢNH 10 – CUỐN NHẬT KÝ 50 NĂM
Hình ảnh: Minh phá khóa và bước vào. Một chiếc bàn phủ bụi nằm giữa phòng. Trên bàn là cuốn nhật ký đã ố vàng. Anh mở từng trang, những dòng chữ run rẩy hiện ra.
Camera: Top-down shot vào cuốn nhật ký, chuyển sang close-up từng dòng chữ.
Lời dẫn: “Trong căn phòng ấy, Minh tìm thấy một cuốn nhật ký cũ. Trang cuối cùng ghi lại một sự thật kinh hoàng: Ngày 17 tháng 10. Con gái tôi vẫn đang ở trong căn phòng này. Tôi đã khóa cửa lại. Nhưng đêm nào nó cũng khóc. Nó nói rằng… người chết trong nhà không phải là nó.”

PHÂN CẢNH 11 – SỰ THẬT BỊ CHÔN GIẤU
Hình ảnh: Những đoạn ký ức chớp nhoáng hiện ra: người đàn ông trong ảnh đóng sầm cửa phòng, người phụ nữ khóc lóc, cô bé đập cửa trong tuyệt vọng. Sau đó, ngọn đèn dầu tắt phụt.
Camera: Flashback montage, handheld camera, dramatic cuts.
Lời dẫn: “Minh bắt đầu hiểu ra. Năm mươi năm trước, một bi kịch đã xảy ra trong căn nhà này. Một cô bé bị nhốt trong căn phòng tối suốt nhiều ngày. Nhưng người dân trong làng lại được thông báo rằng cô bé đã chết vì bệnh.”

PHÂN CẢNH 12 – NGƯỜI ĐÀN BÀ CUỐI HÀNH LANG
Hình ảnh: Minh bước ra khỏi phòng. Ở cuối hành lang xuất hiện một người phụ nữ mặc áo trắng, mái tóc dài che kín mặt. Bà đứng bất động, hai tay buông thõng.
Camera: Long shot, slow zoom-in.
Lời dẫn: “Nhưng trước khi Minh kịp rời đi, một bóng người xuất hiện ở cuối hành lang. Đó là một người phụ nữ mặc áo trắng. Bà ta đứng im lặng… nhìn thẳng vào anh.”

PHÂN CẢNH 13 – ĐỪNG NGOẢNH ĐẦU
Hình ảnh: Minh nghe thấy tiếng bước chân phía sau. Anh chạy dọc hành lang, những cánh cửa liên tục đóng sầm. Tiếng thì thầm ngày càng gần.
Camera: Handheld chase shot, rapid cuts, slight motion blur.
Lời dẫn: “Anh lao về phía cửa chính. Nhưng càng chạy, hành lang càng trở nên dài hơn. Và giọng nói ấy vẫn không ngừng gọi tên anh: Minh… đừng đi… Minh… quay lại nhìn mẹ đi con…”

PHÂN CẢNH 14 – KHUÔN MẶT TRONG GƯƠNG
Hình ảnh: Minh vô tình nhìn vào chiếc gương cũ treo trên tường. Trong gương, phía sau anh không phải người phụ nữ áo trắng… mà là một bé gái đang đứng sát lưng anh, khuôn mặt đầy vết bầm tím.
Camera: Mirror reflection reveal, extreme close-up.
Lời dẫn: “Trong khoảnh khắc tuyệt vọng, Minh nhìn thấy một thứ khiến anh chết lặng. Trong gương, người đứng sau lưng anh không phải người phụ nữ. Mà là cô bé trong bức ảnh gia đình.”

PHÂN CẢNH 15 – CÚ TWIST
Hình ảnh: Bé gái từ từ ngẩng đầu. Gương mặt cô bé giống hệt Minh. Căn phòng rung chuyển, những tấm ảnh trên tường rơi xuống. Một tấm ảnh cũ hiện rõ: cô bé đứng cạnh người đàn ông, trên mặt sau ghi dòng chữ: “Con gái yêu – Minh”.
Camera: Slow push-in vào tấm ảnh, sau đó hard cut sang khuôn mặt Minh.
Lời dẫn: “Nhưng sự thật còn kinh hoàng hơn. Cô bé ấy không phải một người xa lạ. Cô chính là Minh… trong một ký ức mà anh đã bị buộc phải quên từ khi còn nhỏ. Và người đàn bà kia… chính là mẹ anh.”

PHÂN CẢNH 16 – NGƯỜI TIẾP THEO
Hình ảnh: Sáng hôm sau, căn nhà vẫn im lìm. Cánh cửa khép kín. Một người dân đi ngang qua nhìn vào cửa sổ. Bên trong, ngọn đèn dầu vẫn cháy. Trên bàn thờ xuất hiện một bức ảnh mới: Minh đang mỉm cười, đứng cạnh cô bé trong bức ảnh cũ.
Camera: Slow pull-back khỏi căn nhà, dần chìm vào màn sương.
Lời dẫn: “Sáng hôm sau, Minh biến mất. Không ai tìm thấy anh. Chỉ có một bức ảnh mới xuất hiện trên bàn thờ. Và kể từ đêm đó, mỗi khi đồng hồ điểm mười hai giờ… người ta lại nghe thấy hai giọng nói thì thầm bên trong căn nhà: Mẹ ơi… tối nay có khách mới.”`;

    const scenesData = [
      { order: 1, title: 'Lời Cảnh Báo', dur: 9.5, cam: 'slow_push_in', desc: 'Flycam lướt qua ngôi làng hẻo lánh và căn nhà gỗ cô độc trong sương mù', narr: 'Bạn có dám bước chân vào căn nhà gỗ cổ kính ở cuối làng, nơi mà ngay cả những người gan dạ nhất cũng không dám đi ngang qua sau khi trời tối?' },
      { order: 2, title: 'Ngôi Nhà Bị Lãng Quên', dur: 10.0, cam: 'pan_left', desc: 'Căn nhà gỗ mục nát, xích đu cũ kỹ trước sân tự chuyển động trong gió lạnh', narr: 'Người dân kể rằng, căn nhà ấy đã bị bỏ hoang gần năm mươi năm. Không ai biết chủ nhân cuối cùng của nó là ai. Nhưng có một điều tất cả đều biết…' },
      { order: 3, title: 'Ngọn Đèn Lúc Nửa Đêm', dur: 11.0, cam: 'push_in', desc: 'Đồng hồ quả lắc điểm đúng 00:00, ngọn đèn dầu trên bàn thờ đột nhiên bốc cháy', narr: 'Cứ đúng mười hai giờ đêm, ngọn đèn dầu trên bàn thờ lại tự động bốc cháy. Dù không có ai châm lửa. Dù căn nhà đã không còn điện hay người ở từ hàng chục năm trước.' },
      { order: 4, title: 'Tiếng Bước Chân', dur: 10.5, cam: 'tracking', desc: 'Hành lang tối om, sàn gỗ kẽo kẹt và từng dấu chân ướt hiện dần trên sàn', narr: 'Nhưng điều đáng sợ nhất không phải ngọn đèn. Mà là tiếng bước chân. Đêm nào cũng vậy, cứ sau khi ngọn đèn sáng lên, lại có ai đó đi lại trong căn nhà.' },
      { order: 5, title: 'Người Khách Không Mời', dur: 12.0, cam: 'slow_push_in', desc: 'Minh cầm đèn pin và máy quay bước vào khám phá sự thật', narr: 'Một đêm nọ, Minh – chàng trai trẻ vừa trở về làng – quyết định tự mình khám phá bí mật ấy. Anh mang theo máy quay, đèn pin và một chiếc điện thoại. Anh tin rằng mọi câu chuyện ma quỷ đều có lời giải thích.' },
      { order: 6, title: 'Cánh Cửa Tự Mở', dur: 10.5, cam: 'pan_right', desc: 'Cánh cửa gỗ tự mở với tiếng rít dài, căn phòng phủ bụi và khung ảnh cũ nghiêng', narr: 'Nhưng ngay khi anh vừa chạm vào cánh cửa, nó đã tự mở ra. Bên trong, mọi thứ vẫn được giữ nguyên như thể chủ nhân căn nhà chỉ vừa rời đi vài phút trước.' },
      { order: 7, title: 'Bức Ảnh Kỳ Lạ', dur: 9.5, cam: 'push_in', desc: 'Minh soi đèn vào bức ảnh gia đình có gương mặt bé gái bị cào xước nát', narr: 'Trên tường là bức ảnh của một gia đình ba người. Nhưng kỳ lạ thay, khuôn mặt cô bé trong ảnh đã bị ai đó cố tình cào nát.' },
      { order: 8, title: 'Tiếng Thì Thầm', dur: 8.5, cam: 'static', desc: 'Minh quay đầu về cầu thang, giọng nữ thì thầm sau gáy và đèn pin tắt phụt', narr: 'Bỗng nhiên, một giọng nói rất nhỏ vang lên ngay sau lưng anh… Minh… cuối cùng anh cũng về rồi…' },
      { order: 9, title: 'Căn Phòng Khóa Kín', dur: 11.0, cam: 'slow_push_in', desc: 'Căn phòng nhỏ gầm cầu thang có ổ khóa rỉ sét và hàng chục vết cào từ trong ra', narr: 'Anh lần theo âm thanh và phát hiện một căn phòng nhỏ bị khóa kín dưới gầm cầu thang. Trên cánh cửa là hàng chục vết cào sâu. Điều đáng sợ là… tất cả đều hướng từ bên trong ra ngoài.' },
      { order: 10, title: 'Cuốn Nhật Ký 50 Năm', dur: 14.0, cam: 'push_in', desc: 'Cuốn nhật ký ố vàng với trang cuối: Người chết trong nhà không phải là nó', narr: 'Trong căn phòng ấy, Minh tìm thấy một cuốn nhật ký cũ. Trang cuối cùng ghi lại một sự thật kinh hoàng: Ngày 17 tháng 10. Con gái tôi vẫn đang ở trong căn phòng này. Tôi đã khóa cửa lại. Nhưng đêm nào nó cũng khóc. Nó nói rằng… người chết trong nhà không phải là nó.' },
      { order: 11, title: 'Sự Thật Bị Chôn Giấu', dur: 13.0, cam: 'pan_left', desc: 'Ký ức chớp nhoáng: người đàn ông đóng sầm cửa, người phụ nữ khóc, cô bé đập cửa', narr: 'Minh bắt đầu hiểu ra. Năm mươi năm trước, một bi kịch đã xảy ra trong căn nhà này. Một cô bé bị nhốt trong căn phòng tối suốt nhiều ngày. Nhưng người dân trong làng lại được thông báo rằng cô bé đã chết vì bệnh.' },
      { order: 12, title: 'Người Đàn Bà Cuối Hành Lang', dur: 10.5, cam: 'slow_push_in', desc: 'Người phụ nữ áo trắng tóc dài che kín mặt đứng bất động cuối hành lang', narr: 'Nhưng trước khi Minh kịp rời đi, một bóng người xuất hiện ở cuối hành lang. Đó là một người phụ nữ mặc áo trắng. Bà ta đứng im lặng… nhìn thẳng vào anh.' },
      { order: 13, title: 'Đừng Ngoảnh Đầu', dur: 11.5, cam: 'tracking', desc: 'Minh chạy dọc hành lang vô tận, các cánh cửa đóng sầm và tiếng thì thầm gọi tên', narr: 'Anh lao về phía cửa chính. Nhưng càng chạy, hành lang càng trở nên dài hơn. Và giọng nói ấy vẫn không ngừng gọi tên anh: Minh… đừng đi… Minh… quay lại nhìn mẹ đi con…' },
      { order: 14, title: 'Khuôn Mặt Trong Gương', dur: 11.0, cam: 'push_in', desc: 'Trong gương, phía sau Minh là cô bé trong bức ảnh với khuôn mặt bầm tím', narr: 'Trong khoảnh khắc tuyệt vọng, Minh nhìn thấy một thứ khiến anh chết lặng. Trong gương, người đứng sau lưng anh không phải người phụ nữ. Mà là cô bé trong bức ảnh gia đình.' },
      { order: 15, title: 'Cú Twist', dur: 12.5, cam: 'slow_push_in', desc: 'Bé gái giống hệt Minh, mặt sau tấm ảnh ghi: Con gái yêu - Minh. Người đàn bà chính là mẹ', narr: 'Nhưng sự thật còn kinh hoàng hơn. Cô bé ấy không phải một người xa lạ. Cô chính là Minh… trong một ký ức mà anh đã bị buộc phải quên từ khi còn nhỏ. Và người đàn bà kia… chính là mẹ anh.' },
      { order: 16, title: 'Người Tiếp Theo', dur: 15.0, cam: 'pull_out', desc: 'Sáng hôm sau Minh biến mất, bàn thờ có ảnh mới của Minh: Mẹ ơi, tối nay có khách mới', narr: 'Sáng hôm sau, Minh biến mất. Không ai tìm thấy anh. Chỉ có một bức ảnh mới xuất hiện trên bàn thờ. Và kể từ đêm đó, mỗi khi đồng hồ điểm mười hai giờ… người ta lại nghe thấy hai giọng nói thì thầm bên trong căn nhà: Mẹ ơi… tối nay có khách mới.' },
    ];

    let curF = 0;
    const horrorScenes = scenesData.map((sd) => {
      const fCount = Math.round(sd.dur * 30);
      const sc: SceneItem = {
        scene_id: `scene_${String(sd.order).padStart(3, '0')}`,
        scene_order: sd.order,
        chapter_order: Math.ceil(sd.order / 4),
        scene_type: sd.order === 1 ? 'hook' : sd.order === 15 ? 'twist' : sd.order === 16 ? 'cta' : 'narrative',
        narration_text: sd.narr,
        duration_seconds: sd.dur,
        start_frame: curF,
        end_frame: curF + fCount,
        visual_method: 'horror',
        visual_description: sd.desc,
        camera_direction: sd.cam as any,
        visual_config: {},
        subtitles_json: [],
        assets: [],
      };
      curF += fCount;
      return sc;
    });

    const totalDur = horrorScenes.reduce((a, s) => a + s.duration_seconds, 0);

    return {
      topic: title || 'Căn Nhà Gỗ Cuối Làng',
      script,
      manifest: {
        episode_id: episodeId,
        title: title || 'Căn Nhà Gỗ Cuối Làng',
        genre: 'horror',
        video_format: videoType,
        aspect_ratio,
        total_duration_sec: totalDur,
        total_frames: curF,
        voice_config: { voice: 'vi-VN-NamMinhNeural', rate: '+0%', pitch: '+0Hz' },
        video_specs: { width, height, fps: 30 },
        audio_specs: { target_lufs: -14.0, true_peak: -1.0 },
        scenes: horrorScenes,
      }
    };
  }

  if (g.includes('anatomy') || t.includes('tim') || t.includes('giải phẫu') || t.includes('nội tạng')) {
    const script = `Bạn có biết rằng, trung bình mỗi ngày, trái tim con người đập hơn một trăm nghìn lần? Trái tim hoạt động như một cỗ máy bơm sinh học phi thường, co bóp theo chu kỳ nhịp nhàng bảy mươi hai nhịp mỗi phút. Với bốn buồng tim phối hợp chính xác, nó đẩy dòng máu giàu oxy qua quai động mạch chủ đi nuôi dưỡng toàn bộ cơ thể!`;
    return {
      topic: title || 'Giải Phẫu Hệ Cơ Quan & Trái Tim Sinh Học',
      script,
      manifest: {
        episode_id: episodeId,
        title: title || 'Giải Phẫu Hệ Cơ Quan & Trái Tim Sinh Học',
        genre: 'anatomy',
        video_format: videoType,
        aspect_ratio,
        total_duration_sec: 22.0,
        total_frames: 660,
        voice_config: { voice: 'vi-VN-MaiNgocNeural', rate: '+0%', pitch: '+5Hz' },
        video_specs: { width, height, fps: 30 },
        audio_specs: { target_lufs: -14.0, true_peak: -1.0 },
        scenes: [
          {
            scene_order: 1,
            scene_type: 'hook',
            narration_text: 'Bạn có biết rằng, trung bình mỗi ngày, trái tim con người đập hơn một trăm nghìn lần?',
            duration_seconds: 6.5,
            start_frame: 0,
            end_frame: 195,
            visual_method: 'anatomy',
            camera_direction: 'slow_push_in',
            visual_config: {},
            subtitles_json: [],
            assets: [],
          },
          {
            scene_order: 2,
            scene_type: 'body',
            narration_text: 'Trái tim hoạt động như một cỗ máy bơm sinh học phi thường, co bóp theo chu kỳ nhịp nhàng bảy mươi hai nhịp mỗi phút.',
            duration_seconds: 8.0,
            start_frame: 195,
            end_frame: 435,
            visual_method: 'anatomy',
            camera_direction: 'push_in',
            visual_config: {},
            subtitles_json: [],
            assets: [],
          },
          {
            scene_order: 3,
            scene_type: 'resolution',
            narration_text: 'Với bốn buồng tim phối hợp chính xác, nó đẩy dòng máu giàu oxy qua quai động mạch chủ đi nuôi dưỡng toàn bộ cơ thể!',
            duration_seconds: 7.5,
            start_frame: 435,
            end_frame: 660,
            visual_method: 'anatomy',
            camera_direction: 'static',
            visual_config: {},
            subtitles_json: [],
            assets: [],
          },
        ]
      }
    };
  }

  if (g.includes('economics') || t.includes('kinh tế') || t.includes('tài chính') || t.includes('lạm phát')) {
    const script = `Nền kinh tế Việt Nam năm 2024 đang ghi nhận những bước chuyển mình mạnh mẽ với mục tiêu tăng trưởng GDP bứt phá. Làn sóng vốn đầu tư trực tiếp nước ngoài FDI đạt kỷ lục mới, cùng sự phục hồi mạnh mẽ của kim ngạch xuất khẩu công nghệ cao. Đây chính là động lực quan trọng đưa Việt Nam vươn lên thành trung tâm sản xuất chiến lược của khu vực!`;
    return {
      topic: title || 'Tăng Trưởng Kinh Tế Việt Nam 2024',
      script,
      manifest: {
        episode_id: episodeId,
        title: title || 'Tăng Trưởng Kinh Tế Việt Nam 2024',
        genre: 'economics',
        video_format: videoType,
        aspect_ratio,
        total_duration_sec: 24.0,
        total_frames: 720,
        voice_config: { voice: 'vi-VN-NamMinhNeural', rate: '+0%', pitch: '+0Hz' },
        video_specs: { width, height, fps: 30 },
        audio_specs: { target_lufs: -14.0, true_peak: -1.0 },
        scenes: [
          {
            scene_order: 1,
            scene_type: 'hook',
            narration_text: 'Nền kinh tế Việt Nam năm 2024 đang ghi nhận những bước chuyển mình mạnh mẽ với mục tiêu tăng trưởng GDP bứt phá.',
            duration_seconds: 7.5,
            start_frame: 0,
            end_frame: 225,
            visual_method: 'infographic',
            camera_direction: 'slow_push_in',
            visual_config: {},
            subtitles_json: [],
            assets: [],
          },
          {
            scene_order: 2,
            scene_type: 'body',
            narration_text: 'Làn sóng vốn đầu tư trực tiếp nước ngoài FDI đạt kỷ lục mới, cùng sự phục hồi mạnh mẽ của kim ngạch xuất khẩu công nghệ cao.',
            duration_seconds: 8.5,
            start_frame: 225,
            end_frame: 480,
            visual_method: 'infographic',
            camera_direction: 'pan_right',
            visual_config: {},
            subtitles_json: [],
            assets: [],
          },
          {
            scene_order: 3,
            scene_type: 'resolution',
            narration_text: 'Đây chính là động lực quan trọng đưa Việt Nam vươn lên thành trung tâm sản xuất chiến lược của khu vực!',
            duration_seconds: 8.0,
            start_frame: 480,
            end_frame: 720,
            visual_method: 'infographic',
            camera_direction: 'pull_out',
            visual_config: {},
            subtitles_json: [],
            assets: [],
          },
        ]
      }
    };
  }

  if (g.includes('science') || t.includes('cầu') || t.includes('khoa học') || t.includes('vật lý') || t.includes('vũ trụ')) {
    const script = `Năm 1831, cây cầu treo Broughton tại nước Anh đã bất ngờ đổ sập khi một đoàn quân duyệt binh bước đều qua cầu. Hiện tượng vật lý nào đã gây ra thảm họa này? Đó chính là sự cộng hưởng dao động cơ học. Khi tần số bước chân trùng khớp với tần số dao động tự nhiên của cây cầu, biên độ rung lắc đã tăng vọt ngoài tầm kiểm soát!`;
    return {
      topic: title || 'Nguyên Lý Cộng Hưởng Cầu Broughton',
      script,
      manifest: {
        episode_id: episodeId,
        title: title || 'Nguyên Lý Cộng Hưởng Cầu Broughton',
        genre: 'science',
        video_format: videoType,
        aspect_ratio,
        total_duration_sec: 25.0,
        total_frames: 750,
        voice_config: { voice: 'vi-VN-MaiNgocNeural', rate: '+0%', pitch: '+5Hz' },
        video_specs: { width, height, fps: 30 },
        audio_specs: { target_lufs: -14.0, true_peak: -1.0 },
        scenes: [
          {
            scene_order: 1,
            scene_type: 'hook',
            narration_text: 'Năm 1831, cây cầu treo Broughton tại nước Anh đã bất ngờ đổ sập khi một đoàn quân duyệt binh bước đều qua cầu.',
            duration_seconds: 7.5,
            start_frame: 0,
            end_frame: 225,
            visual_method: 'schematic',
            camera_direction: 'slow_push_in',
            visual_config: {},
            subtitles_json: [],
            assets: [],
          },
          {
            scene_order: 2,
            scene_type: 'body',
            narration_text: 'Hiện tượng vật lý nào đã gây ra thảm họa này? Đó chính là sự cộng hưởng dao động cơ học.',
            duration_seconds: 8.0,
            start_frame: 225,
            end_frame: 465,
            visual_method: 'schematic',
            camera_direction: 'pan_left',
            visual_config: {},
            subtitles_json: [],
            assets: [],
          },
          {
            scene_order: 3,
            scene_type: 'resolution',
            narration_text: 'Khi tần số bước chân trùng khớp với tần số dao động tự nhiên của cây cầu, biên độ rung lắc đã tăng vọt ngoài tầm kiểm soát!',
            duration_seconds: 9.5,
            start_frame: 465,
            end_frame: 750,
            visual_method: 'schematic',
            camera_direction: 'pull_out',
            visual_config: {},
            subtitles_json: [],
            assets: [],
          },
        ]
      }
    };
  }

  // Default: Historical Document (Điện Biên Phủ)
  const defaultScript = `Bạn có biết rằng, cách đây hơn 70 năm, tại một thung lũng lòng chảo ở Tây Bắc, quân và dân Việt Nam đã làm nên một kỳ tích chấn động địa cầu? Đó chính là chiến thắng Điện Biên Phủ lịch sử năm 1954. Dưới sự chỉ huy tài ba của Đại tướng Võ Nguyên Giáp, toàn quân ta đã kiên cường vượt mọi gian khổ, kéo pháo qua đèo cao, bạt núi mở đường để làm nên chiến công hiển hách lừng lẫy năm châu. Ngày 7 tháng 5 năm 1954, lá cờ Quyết chiến Quyết thắng tung bay trên nóc hầm De Castries, đánh dấu mốc son chói lọi trong lịch sử dân tộc! Hãy bấm đăng ký kênh để đón xem những câu chuyện lịch sử tự hào tiếp theo!`;
  return {
    topic: title || 'Chiến Thắng Điện Biên Phủ 1954',
    script: defaultScript,
    manifest: {
      episode_id: episodeId,
      title: title || 'Chiến Thắng Điện Biên Phủ 1954',
      genre: 'historical_doc',
      video_format: videoType,
      aspect_ratio,
      total_duration_sec: 40.0,
      total_frames: 1200,
      voice_config: { voice: 'vi-VN-NamMinhNeural', rate: '+0%', pitch: '+0Hz' },
      video_specs: { width, height, fps: 30 },
      audio_specs: { target_lufs: -14.0, true_peak: -1.0 },
      scenes: [
        {
          scene_order: 1,
          scene_type: 'hook',
          narration_text: 'Bạn có biết rằng, cách đây hơn 70 năm, tại một thung lũng lòng chảo ở Tây Bắc, quân và dân Việt Nam đã làm nên một kỳ tích chấn động địa cầu?',
          duration_seconds: 7.5,
          start_frame: 0,
          end_frame: 225,
          visual_method: 'map',
          camera_direction: 'slow_push_in',
          visual_config: {},
          subtitles_json: [],
          assets: [],
        },
        {
          scene_order: 2,
          scene_type: 'context',
          narration_text: 'Đó chính là chiến thắng Điện Biên Phủ lịch sử năm 1954. Dưới sự chỉ huy tài ba của Đại tướng Võ Nguyên Giáp, toàn quân ta đã kiên cường vượt mọi gian khổ.',
          duration_seconds: 9.0,
          start_frame: 225,
          end_frame: 495,
          visual_method: 'toon',
          camera_direction: 'pan_left',
          visual_config: {},
          subtitles_json: [],
          assets: [],
        },
        {
          scene_order: 3,
          scene_type: 'climax',
          narration_text: 'Toàn quân đã kéo pháo qua đèo cao, bạt núi mở đường để làm nên chiến công hiển hách lừng lẫy năm châu chấn động địa cầu.',
          duration_seconds: 8.5,
          start_frame: 495,
          end_frame: 750,
          visual_method: 'toon',
          camera_direction: 'push_in',
          visual_config: {},
          subtitles_json: [],
          assets: [],
        },
        {
          scene_order: 4,
          scene_type: 'resolution',
          narration_text: 'Ngày 7 tháng 5 năm 1954, lá cờ Quyết chiến Quyết thắng tung bay trên nóc hầm De Castries, đánh dấu mốc son chói lọi trong lịch sử dân tộc!',
          duration_seconds: 9.5,
          start_frame: 750,
          end_frame: 1035,
          visual_method: 'toon',
          camera_direction: 'pull_out',
          visual_config: {},
          subtitles_json: [],
          assets: [],
        },
        {
          scene_order: 5,
          scene_type: 'cta',
          narration_text: 'Hãy bấm đăng ký kênh để đón xem những câu chuyện lịch sử tự hào tiếp theo!',
          duration_seconds: 5.5,
          start_frame: 1035,
          end_frame: 1200,
          visual_method: 'toon',
          camera_direction: 'static',
          visual_config: {},
          subtitles_json: [],
          assets: [],
        },
      ]
    }
  };
};

const DEFAULT_SCRIPT = `Bạn có biết rằng, cách đây hơn 70 năm, tại một thung lũng lòng chảo ở Tây Bắc, quân và dân Việt Nam đã làm nên một kỳ tích chấn động địa cầu? Đó chính là chiến thắng Điện Biên Phủ lịch sử năm 1954. Dưới sự chỉ huy tài ba của Đại tướng Võ Nguyên Giáp, toàn quân ta đã kiên cường vượt mọi gian khổ, kéo pháo qua đèo cao, bạt núi mở đường để làm nên chiến công hiển hách lừng lẫy năm châu. Ngày 7 tháng 5 năm 1954, lá cờ Quyết chiến Quyết thắng tung bay trên nóc hầm De Castries, đánh dấu mốc son chói lọi trong lịch sử dân tộc! Hãy bấm đăng ký kênh để đón xem những câu chuyện lịch sử tự hào tiếp theo!`;

const DEFAULT_VOICES: VoiceInfo[] = [
  { id: 'vi-VN-NamMinhNeural', name: 'Nam Minh (Giọng Nam - Trầm Ấm Chuẩn)', display_name: 'Nam Minh (Nam Bắc)', gender: 'Male', locale: 'vi-VN' },
  { id: 'vi-VN-HoaiMyNeural', name: 'Hoài My (Giọng Nữ - Truyền Cảm Ấm Áp)', display_name: 'Hoài My (Nữ Bắc)', gender: 'Female', locale: 'vi-VN' },
  { id: 'vi-VN-NamGiapNeural', name: 'Nam Giáp (Giọng Nam - Hào Hùng Sử Thi)', display_name: 'Nam Giáp (Nam Bắc - Hào Hùng)', gender: 'Male', locale: 'vi-VN' },
  { id: 'vi-VN-MaiNgocNeural', name: 'Mai Ngọc (Giọng Nữ - Sôi Nổi & Khoa Học)', display_name: 'Mai Ngọc (Nữ Bắc - Tươi Sáng)', gender: 'Female', locale: 'vi-VN' },
];

export const ScriptStudioPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

  const [project, setProject] = useState<Project | null>(null);
  const [scriptText, setScriptText] = useState(DEFAULT_SCRIPT);
  const [selectedGenre, setSelectedGenre] = useState('historical_doc');
  const [videoFormat, setVideoFormat] = useState<'short-form' | 'long-form'>('short-form');
  const [targetDurationSec, setTargetDurationSec] = useState<number>(60);
  const [genres, setGenres] = useState<GenreInfo[]>([]);
  const [voices, setVoices] = useState<VoiceInfo[]>(DEFAULT_VOICES);
  const [voiceVoice, setVoiceVoice] = useState('vi-VN-NamMinhNeural');
  const [voiceRate, setVoiceRate] = useState('+0%');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isGeneratingMovie, setIsGeneratingMovie] = useState(false);
  const [isSynthesizingVoice, setIsSynthesizingVoice] = useState(false);
  const [isDiscoveringAssets, setIsDiscoveringAssets] = useState(false);
  const [isVoiceTesting, setIsVoiceTesting] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [activeSceneIndex, setActiveSceneIndex] = useState(0);
  const [editorMode, setEditorMode] = useState<'timeline' | 'cards'>('timeline');
  const [currentTimeSec, setCurrentTimeSec] = useState<number>(0);
  const [showRenderModal, setShowRenderModal] = useState(false);
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  // VoiceStudio Settings Modal State
  const [showVoiceStudioModal, setShowVoiceStudioModal] = useState(false);
  const [voiceStudioUrl, setVoiceStudioUrl] = useState('http://127.0.0.1:3900');
  const [engineMode, setEngineMode] = useState<'auto' | 'voicestudio' | 'edgetts'>('auto');
  const [voiceStudioOnline, setVoiceStudioOnline] = useState<boolean | null>(null);
  const [isCheckingVS, setIsCheckingVS] = useState(false);

  useEffect(() => {
    apiClient.fetchTTSSettings().then(res => {
      if (res.voicestudio_url) setVoiceStudioUrl(res.voicestudio_url);
      if (res.engine_mode) setEngineMode(res.engine_mode);
      setVoiceStudioOnline(res.voicestudio_online);
    }).catch(err => console.warn('Could not load TTS settings:', err));
  }, []);

  const handleCheckVoiceStudio = async () => {
    setIsCheckingVS(true);
    try {
      const res = await apiClient.checkVoiceStudioStatus();
      setVoiceStudioOnline(res.online);
      setNotice(res.online ? '🟢 VoiceStudio đang hoạt động trực tuyến!' : '🟡 VoiceStudio chưa mở (hệ thống tự động dùng Edge-TTS)');
    } catch (e: any) {
      setVoiceStudioOnline(false);
      setNotice('🟡 Không thể kết nối VoiceStudio (dùng Edge-TTS tự động)');
    } finally {
      setIsCheckingVS(false);
      setTimeout(() => setNotice(null), 3500);
    }
  };

  const handleSaveVoiceStudioSettings = async () => {
    try {
      await apiClient.updateTTSSettings({
        voicestudio_url: voiceStudioUrl,
        engine_mode: engineMode,
      });
      setNotice('Đã lưu cấu hình VoiceStudio thành công!');
      setShowVoiceStudioModal(false);
    } catch (e: any) {
      setNotice(`Lỗi lưu cấu hình: ${e.message}`);
    } finally {
      setTimeout(() => setNotice(null), 3000);
    }
  };

  // Research State
  const [topicQuery, setTopicQuery] = useState('Chiến thắng Điện Biên Phủ 1954');
  const [isResearching, setIsResearching] = useState(false);
  const [researchReport, setResearchReport] = useState<any | null>(null);
  const [showResearchCard, setShowResearchCard] = useState(false);

  // Initial manifest
  const [manifest, setManifest] = useState<SceneManifest>({
    episode_id: projectId || 'demo-ep',
    title: 'Chiến Thắng Điện Biên Phủ 1954',
    genre: 'historical_doc',
    video_format: 'short-form',
    aspect_ratio: '9:16',
    total_duration_sec: 58.0,
    total_frames: 1740,
    voice_config: {
      voice: 'vi-VN-NamMinhNeural',
      rate: '+0%',
      pitch: '+0Hz',
    },
    video_specs: {
      width: 1080,
      height: 1920,
      fps: 30,
    },
    audio_specs: {
      target_lufs: -14.0,
      true_peak: -1.0,
    },
    scenes: [
      {
        scene_order: 1,
        scene_type: 'hook',
        narration_text: 'Bạn có biết rằng, cách đây hơn 70 năm, tại một thung lũng lòng chảo ở Tây Bắc, quân và dân Việt Nam đã làm nên một kỳ tích chấn động địa cầu?',
        duration_seconds: 7.5,
        start_frame: 0,
        end_frame: 225,
        visual_method: 'map',
        visual_config: {},
        subtitles_json: [],
        assets: [],
      },
      {
        scene_order: 2,
        scene_type: 'context',
        narration_text: 'Đó chính là chiến thắng Điện Biên Phủ lịch sử năm 1954. Dưới sự chỉ huy tài ba của Đại tướng Võ Nguyên Giáp, toàn quân ta đã kiên cường vượt mọi gian khổ.',
        duration_seconds: 9.0,
        start_frame: 225,
        end_frame: 495,
        visual_method: 'toon',
        visual_config: {},
        subtitles_json: [],
        assets: [],
      },
      {
        scene_order: 3,
        scene_type: 'climax',
        narration_text: 'Toàn quân đã kéo pháo qua đèo cao, bạt núi mở đường để làm nên chiến công hiển hách lừng lẫy năm châu chấn động địa cầu.',
        duration_seconds: 8.5,
        start_frame: 495,
        end_frame: 750,
        visual_method: 'toon',
        visual_config: {},
        subtitles_json: [],
        assets: [],
      },
      {
        scene_order: 4,
        scene_type: 'resolution',
        narration_text: 'Ngày 7 tháng 5 năm 1954, lá cờ Quyết chiến Quyết thắng tung bay trên nóc hầm De Castries, đánh dấu mốc son chói lọi trong lịch sử dân tộc!',
        duration_seconds: 9.5,
        start_frame: 750,
        end_frame: 1035,
        visual_method: 'toon',
        visual_config: {},
        subtitles_json: [],
        assets: [],
      },
      {
        scene_order: 5,
        scene_type: 'cta',
        narration_text: 'Hãy bấm đăng ký kênh để đón xem những câu chuyện lịch sử tự hào tiếp theo!',
        duration_seconds: 5.0,
        start_frame: 1035,
        end_frame: 1185,
        visual_method: 'toon',
        visual_config: {},
        subtitles_json: [],
        assets: [],
      },
    ],
  });

  const wordCount = scriptText.trim().split(/\s+/).filter(Boolean).length;
  const currentGenreObj = genres.find(g => g.genre_id === selectedGenre);
  const syllablesPerSec = currentGenreObj?.syllables_per_second || 3.8;
  const estimatedDurationSec = Math.round(wordCount / (syllablesPerSec / 1.15));

  useEffect(() => {
    loadInitialData();
  }, [projectId]);

  const loadInitialData = async () => {
    // 1. Load Genres & Voices
    const [fetchedGenres, fetchedVoices] = await Promise.all([
      apiClient.fetchGenres(),
      apiClient.fetchVoices(),
    ]);
    setGenres(fetchedGenres);
    setVoices(fetchedVoices);

    // 2. Load Project if given
    if (projectId) {
      let loadedProj: Project | null = null;
      try {
        loadedProj = await apiClient.getProject(projectId);
      } catch (e) {
        console.warn('Could not load project from API, checking local storage:', e);
        const local = localStorage.getItem('demo_projects');
        if (local) {
          try {
            const list: Project[] = JSON.parse(local);
            loadedProj = list.find((p) => p.id === projectId) || null;
          } catch {
            // ignore
          }
        }
      }

      if (loadedProj) {
        setProject(loadedProj);
        const pGenre = loadedProj.genre || 'general';
        const pType = loadedProj.video_type || 'short-form';
        setSelectedGenre(pGenre);
        setVideoFormat(pType);
        handleFormatChange(pType);

        // Check if user already has a saved manifest/script for this specific project
        const savedManifestKey = `studio_manifest_${projectId}`;
        const savedScriptKey = `studio_script_${projectId}`;
        const localSavedManifest = localStorage.getItem(savedManifestKey);
        const localSavedScript = localStorage.getItem(savedScriptKey);

        if (localSavedManifest) {
          try {
            const parsedManifest = JSON.parse(localSavedManifest);
            setManifest(parsedManifest);
            if (localSavedScript) {
              setScriptText(localSavedScript);
            }
            setTopicQuery(parsedManifest.title || loadedProj.title);
            return;
          } catch (err) {
            console.warn('Failed to parse saved manifest:', err);
          }
        }

        // Initialize tailored default manifest & script for this project's genre and title
        const tmpl = buildDefaultManifestForProject(loadedProj.title, pGenre, pType, projectId);
        setManifest(tmpl.manifest);
        setScriptText(tmpl.script);
        setTopicQuery(tmpl.topic);
        localStorage.setItem(savedManifestKey, JSON.stringify(tmpl.manifest));
        localStorage.setItem(savedScriptKey, tmpl.script);
      }
    }
  };

  const handleFormatChange = (fmt: 'short-form' | 'long-form') => {
    setVideoFormat(fmt);
    const isLong = fmt === 'long-form';
    if (isLong && targetDurationSec < 120) {
      setTargetDurationSec(180);
    } else if (!isLong && targetDurationSec > 90) {
      setTargetDurationSec(60);
    }
    setManifest(prev => ({
      ...prev,
      video_format: fmt,
      aspect_ratio: isLong ? '16:9' : '9:16',
      video_specs: {
        width: isLong ? 1920 : 1080,
        height: isLong ? 1080 : 1920,
        fps: 30,
      }
    }));
  };

  const parseClientScreenplay = (rawText: string) => {
    const sceneRegex = /^\s*(?:PHÂN CẢNH|CẢNH|SCENE)\s+(\d+)[\s:–—]*(.*?)$/gim;
    const matches = [...rawText.matchAll(sceneRegex)];
    if (matches.length === 0) return null;

    const headerRegex = /^\s*(?:Hình ảnh|Camera|Âm thanh|Lời dẫn|Giọng nữ thì thầm|Giọng đọc nhật ký|Thoại|Kết thúc[^\n]*)\s*:/gim;
    const scenes: any[] = [];

    for (let i = 0; i < matches.length; i++) {
      const m = matches[i];
      const num = parseInt(m[1], 10);
      const title = m[2].replace(/[–—:-]/g, '').trim();
      const startIdx = m.index! + m[0].length;
      const endIdx = i + 1 < matches.length ? matches[i + 1].index! : rawText.length;
      let block = rawText.slice(startIdx, endIdx).trim();

      const footerPos = block.indexOf('🎧');
      if (footerPos !== -1) block = block.slice(0, footerPos).trim();

      const headerMatches = [...block.matchAll(headerRegex)];
      let visual = '';
      let camera = '';
      let sound = '';
      const narrations: string[] = [];

      for (let hIdx = 0; hIdx < headerMatches.length; hIdx++) {
        const hm = headerMatches[hIdx];
        const hTitle = hm[0].toLowerCase();
        const contentStart = hm.index! + hm[0].length;
        const contentEnd = hIdx + 1 < headerMatches.length ? headerMatches[hIdx + 1].index! : block.length;
        const content = block.slice(contentStart, contentEnd).trim();

        if (hTitle.includes('hình ảnh')) {
          visual = content;
        } else if (hTitle.includes('camera')) {
          camera = content;
        } else if (hTitle.includes('âm thanh')) {
          sound = content;
        } else if (hTitle.includes('lời dẫn') || hTitle.includes('giọng') || hTitle.includes('thoại') || hTitle.includes('kết thúc')) {
          const clean = content.replace(/^[“"''‘]+|[”"''’]+$/g, '').trim();
          if (clean) narrations.push(clean);
        }
      }

      const narration = narrations.length > 0 ? narrations.join(' ') : title;
      scenes.push({
        order: num,
        title,
        visual,
        camera,
        sound,
        narration,
      });
    }
    return scenes;
  };

  const handleAnalyzeScript = async () => {
    if (!scriptText.trim()) return;
    setIsAnalyzing(true);
    setNotice(null);

    try {
      let data: any = null;
      try {
        data = await apiClient.analyzeScript({
          script_text: scriptText,
          target_duration_seconds: targetDurationSec || estimatedDurationSec,
          genre: selectedGenre,
          video_format: videoFormat,
        });
      } catch (apiErr) {
        console.warn('Backend analyze API error, falling back to local NLP screenplay parser:', apiErr);
      }

      const clientScenes = parseClientScreenplay(scriptText);
      const isLong = videoFormat === 'long-form';
      const fps = 30;
      let currentFrame = 0;

      let rawScenes: any[] = [];
      if (clientScenes && clientScenes.length > 0) {
        rawScenes = clientScenes.map((cs) => {
          const wordCount = cs.narration.split(/\s+/).filter(Boolean).length;
          const durSec = Math.max(4.0, Math.min(18.0, Math.round((wordCount / 2.8) * 10) / 10));
          return {
            scene_order: cs.order,
            scene_type: cs.order === 1 ? 'hook' : cs.order === clientScenes.length ? 'cta' : 'narrative',
            narration_text: cs.narration,
            duration_seconds: durSec,
            visual_method: (selectedGenre === 'horror' || cs.title.toLowerCase().includes('ma') || cs.title.toLowerCase().includes('lời cảnh báo')) ? 'horror' : 'photo',
            visual_description: cs.visual,
            camera_direction: cs.camera || 'slow_push_in',
            suggested_asset_keywords: [cs.title, selectedGenre],
          };
        });
      } else if (data?.scenes && data.scenes.length > 0) {
        rawScenes = data.scenes;
      } else {
        throw new Error('Không thể phân tích kịch bản. Vui lòng kiểm tra định dạng phân cảnh.');
      }

      const convertedScenes: SceneItem[] = rawScenes.map((s: any, idx: number) => {
        const durationSec = Number(s.duration_seconds) || 4.0;
        const frames = Math.round(durationSec * fps);
        const scene: SceneItem = {
          scene_id: s.scene_id || `scene_${String(idx + 1).padStart(3, '0')}`,
          scene_order: s.scene_order || idx + 1,
          chapter_order: s.chapter_order || Math.ceil((idx + 1) / 4),
          scene_type: s.scene_type || 'narrative',
          narration_text: s.narration_text || '',
          duration_seconds: durationSec,
          start_frame: currentFrame,
          end_frame: currentFrame + frames,
          visual_method: s.visual_method || (selectedGenre === 'horror' ? 'horror' : 'photo'),
          visual_description: s.visual_description || '',
          visual_config: {},
          subtitles_json: [],
          assets: (s.suggested_asset_keywords || []).map((k: string, kIdx: number) => ({
            id: `kwd_${kIdx}`,
            asset_type: 'image',
            source_url: '',
            license_type: 'Pending Discovery',
            author_name: k,
            attribution_text: `Từ khóa tìm kiếm: ${k}`
          })),
          camera_direction: s.camera_direction,
          transition: s.transition,
          sound_design: s.sound_design,
          source_references: s.source_references
        };
        currentFrame += frames;
        return scene;
      });

      const totalSec = convertedScenes.reduce((a, s) => a + s.duration_seconds, 0);

      // Extract title from script if formatted like 🎬 CĂN NHÀ GỖ CUỐI LÀNG
      let screenplayTitle = data?.title || project?.title || 'Video AI';
      for (const line of scriptText.split('\n').slice(0, 5)) {
        if (line.includes('🎬')) {
          screenplayTitle = line.replace('🎬', '').trim();
          break;
        }
      }

      setManifest({
        episode_id: projectId || 'ep_active',
        title: screenplayTitle,
        genre: data?.genre || selectedGenre,
        video_format: videoFormat,
        aspect_ratio: isLong ? '16:9' : '9:16',
        total_duration_sec: totalSec,
        total_frames: currentFrame,
        voice_config: {
          voice: voiceVoice,
          rate: voiceRate,
          pitch: '+0Hz',
        },
        video_specs: {
          width: isLong ? 1920 : 1080,
          height: isLong ? 1080 : 1920,
          fps: 30,
        },
        audio_specs: {
          target_lufs: -14.0,
          true_peak: -1.0,
        },
        scenes: convertedScenes,
        chapters: data?.chapters || []
      });

      setNotice(`Phân tích kịch bản thành công theo thể loại ${currentGenreObj?.display_name || selectedGenre}!`);
    } catch (err: any) {
      console.error('Error in analyzeScript:', err);
      setNotice(`Lỗi phân tích: ${err?.message || 'Vui lòng thử lại'}`);
    } finally {
      setIsAnalyzing(false);
      setTimeout(() => setNotice(null), 4000);
    }
  };

  const handleZeroTouchGenerateMovie = async () => {
    if (!scriptText.trim()) return;
    setIsGeneratingMovie(true);
    setNotice('🎬 One-Click Studio: Đang phân tích kịch bản, tạo giọng đọc AI, phối âm 4 bus & bắt đầu kết xuất video...');

    try {
      const result = await apiClient.oneClickProduce({
        script_text: scriptText,
        genre: selectedGenre,
        video_format: videoFormat,
        target_duration_seconds: targetDurationSec,
        voice: voiceVoice,
        rate: voiceRate,
      });

      setManifest(result.manifest);
      setActiveSceneIndex(0);
      setActiveJobId(result.job_id);
      setNotice(`🎬 Đã khởi chạy tiến trình kết xuất video (${result.resolution})!`);
      
      // Automatically trigger HyperFrames rendering modal with active job polling
      setShowRenderModal(true);
    } catch (err: any) {
      console.error('Error in one-click production:', err);
      setNotice(`Lỗi sản xuất phim tự động: ${err?.message || 'Vui lòng thử lại'}`);
    } finally {
      setIsGeneratingMovie(false);
      setTimeout(() => setNotice(null), 5000);
    }
  };

  const handleTestVoice = async () => {
    setIsVoiceTesting(true);
    try {
      const testSample = `Xin chào, đây là giọng đọc AI ${voiceVoice === 'vi-VN-NamMinhNeural' ? 'Nam Minh' : 'Hoài My'} của YTBER Studio.`;
      const tts = await apiClient.synthesizeVoice({
        text: testSample,
        voice: voiceVoice,
        rate: voiceRate,
      });

      // Fetch with auth headers and play via local blob URL for 100% reliable browser preview
      const headers = await getAuthHeaders();
      const res = await fetch(tts.audio_url, { headers });
      if (!res.ok) {
        throw new Error(`Không thể phát âm thanh xem trước (Mã lỗi ${res.status})`);
      }
      const blob = await res.blob();
      const blobUrl = URL.createObjectURL(blob);
      const audio = new Audio(blobUrl);
      audio.onended = () => URL.revokeObjectURL(blobUrl);
      await audio.play();
      setNotice('Đang phát giọng đọc thử nghiệm chất lượng cao...');
    } catch (err: any) {
      setNotice(`Lỗi nghe thử giọng: ${err.message}`);
    } finally {
      setIsVoiceTesting(false);
      setTimeout(() => setNotice(null), 3000);
    }
  };

  const handleGenerateVoiceForScenes = async () => {
    setIsSynthesizingVoice(true);
    setNotice('Đang tổng hợp giọng đọc AI và tạo mốc phụ đề karaoke theo mili-giây...');
    
    try {
      const updatedScenes = [...manifest.scenes];
      let updatedCount = 0;

      for (let i = 0; i < updatedScenes.length; i++) {
        const scene = updatedScenes[i];
        if (!scene.narration_text.trim()) continue;

        try {
          const tts = await apiClient.synthesizeVoice({
            text: scene.narration_text,
            voice: voiceVoice,
            rate: voiceRate,
          });

          const audioFilename = `${tts.audio_id}.mp3`;
          updatedScenes[i] = {
            ...scene,
            audio_id: tts.audio_id,
            audio_filename: audioFilename,
            audio_url: tts.audio_url,
            duration_seconds: Math.max(3.0, tts.duration_seconds),
            subtitles_json: tts.words || [],
          };
          updatedCount++;
        } catch (e) {
          console.warn(`Lỗi tổng hợp giọng cảnh ${i + 1}:`, e);
        }
      }

      // Recalculate frame bounds
      let currF = 0;
      const reCalculated = updatedScenes.map(s => {
        const fCount = Math.round(s.duration_seconds * 30);
        const sc = { ...s, start_frame: currF, end_frame: currF + fCount };
        currF += fCount;
        return sc;
      });

      const totalDur = reCalculated.reduce((a, s) => a + s.duration_seconds, 0);

      setManifest(prev => ({
        ...prev,
        total_duration_sec: totalDur,
        total_frames: currF,
        scenes: reCalculated,
      }));

      setNotice(`Đã tạo giọng đọc & phụ đề mili-giây cho ${updatedCount}/${updatedScenes.length} cảnh!`);
    } catch (e: any) {
      setNotice(`Lỗi tổng hợp giọng đọc: ${e.message}`);
    } finally {
      setIsSynthesizingVoice(false);
      setTimeout(() => setNotice(null), 3500);
    }
  };

  const handleAutoDiscoverAssets = async () => {
    setIsDiscoveringAssets(true);
    setNotice('Đang tự động tìm kiếm và tải tư liệu thực từ Wikimedia & Openverse...');

    try {
      const updatedScenes = [...manifest.scenes];
      let matchedCount = 0;

      for (let i = 0; i < updatedScenes.length; i++) {
        const scene = updatedScenes[i];
        if (scene.assets?.[0]?.local_url) continue;

        const query =
          (scene as any).search_keywords?.[0] ||
          (scene as any).suggested_asset_keywords?.[0] ||
          scene.visual_description?.split(' ')[0] ||
          'Vietnam archival photography';

        try {
          const results = await apiClient.searchAssets(query, 5);
          if (results.length > 0) {
            const topAsset = results[0];
            const downloaded = await apiClient.downloadAsset({
              url: topAsset.source_url,
              title: topAsset.attribution_text?.replace('Ảnh: ', '') || query,
              creator: topAsset.author_name,
              license_type: topAsset.license_type,
              attribution_text: topAsset.attribution_text,
            });

            updatedScenes[i] = {
              ...scene,
              assets: [downloaded],
              visual_config: { ...scene.visual_config, imageUrl: downloaded.local_url }
            };
            matchedCount++;
          }
        } catch (err) {
          console.warn(`Lỗi tìm tư liệu cảnh ${i + 1}:`, err);
        }
      }

      setManifest(prev => ({
        ...prev,
        scenes: updatedScenes,
      }));
      setNotice(`Đã tìm kiếm và ghép thành công tư liệu thực cho ${matchedCount} cảnh!`);
    } catch (err: any) {
      setNotice(`Lỗi tìm tư liệu tự động: ${err.message}`);
    } finally {
      setIsDiscoveringAssets(false);
      setTimeout(() => setNotice(null), 3500);
    }
  };

  const handleSaveProject = async () => {
    setIsSaving(true);
    try {
      if (projectId) {
        localStorage.setItem(`studio_manifest_${projectId}`, JSON.stringify(manifest));
        localStorage.setItem(`studio_script_${projectId}`, scriptText);
        try {
          await apiClient.updateManifest(projectId, manifest);
        } catch (apiErr) {
          console.warn('API updateManifest failed, saved locally:', apiErr);
        }
      }
      setNotice('Đã lưu toàn bộ tiến độ kịch bản vào dự án!');
    } catch (e: any) {
      setNotice(`Lỗi lưu dự án: ${e.message}`);
    } finally {
      setIsSaving(false);
      setTimeout(() => setNotice(null), 2500);
    }
  };

  const handleResearchTopic = async () => {
    if (!topicQuery.trim()) return;
    setIsResearching(true);
    setNotice('Đang tổng hợp thông tin, xác thực nguồn dẫn & lập chiến lược kịch bản...');
    try {
      const report = await apiClient.researchTopic(topicQuery, selectedGenre);
      setResearchReport(report);
      setShowResearchCard(true);
      setNotice(`Đã hoàn tất nghiên cứu chuyên sâu cho chủ đề: ${report.topic}`);
    } catch (err: any) {
      setNotice(`Lỗi nghiên cứu chủ đề: ${err.message}`);
    } finally {
      setIsResearching(false);
      setTimeout(() => setNotice(null), 3500);
    }
  };

  const handleApplyResearchToScript = () => {
    if (!researchReport) return;
    const factsSummary = (researchReport.verified_facts || []).map((f: any) => f.claim).join('. ');
    const hook = researchReport.narrative_strategy?.hook_angle || '';
    const newScript = `${hook} ${factsSummary} Hãy nhấn đăng ký kênh để khám phá thêm những câu chuyện hấp dẫn tiếp theo!`;
    setScriptText(newScript);
    setNotice('Đã cập nhật kịch bản theo dữ liệu nghiên cứu chuyên sâu!');
    setTimeout(() => setNotice(null), 3000);
  };

  return (
    <div className="min-h-screen bg-studio-bg flex flex-col">
      {/* Studio Header Bar */}
      <header className="sticky top-0 z-40 bg-studio-surface/90 backdrop-blur-md border-b border-studio-border px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/')}
            className="w-9 h-9 rounded-xl bg-studio-card hover:bg-studio-border text-gray-400 hover:text-white flex items-center justify-center transition"
            title="Quay lại danh sách dự án"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <h1 className="text-sm font-bold text-white flex items-center gap-2">
              <Film className="w-4 h-4 text-studio-primary" />
              {project?.title || manifest.title || 'Studio Video AI'}
              <span className="text-[10px] bg-studio-primary/20 text-studio-primary border border-studio-primary/30 px-2 py-0.5 rounded-full font-mono uppercase">
                {videoFormat}
              </span>
            </h1>
            <p className="text-[11px] text-gray-400">
              {manifest.aspect_ratio} ({manifest.video_specs.width}×{manifest.video_specs.height}) • 30 FPS • {manifest.scenes.length} cảnh • ~{Math.round(manifest.total_duration_sec)}s
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {notice && (
            <div className="flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 px-3 py-1 rounded-lg animate-fade-in">
              <Check className="w-3.5 h-3.5" />
              <span>{notice}</span>
            </div>
          )}

          <button
            onClick={handleZeroTouchGenerateMovie}
            disabled={isGeneratingMovie}
            className="flex items-center gap-2 bg-gradient-to-r from-emerald-600 via-teal-600 to-indigo-600 hover:from-emerald-500 hover:to-indigo-500 disabled:opacity-50 text-white text-xs font-extrabold px-4 py-2 rounded-xl shadow-lg transition hover:scale-105 border border-emerald-400/40"
          >
            <Sparkles className="w-3.5 h-3.5 text-amber-300 animate-pulse" />
            <span>{isGeneratingMovie ? 'Đang tạo phim tự động...' : '🎬 Tạo Phim Tự Động (Zero-Touch AI)'}</span>
          </button>

          <button
            onClick={() => setShowVoiceStudioModal(true)}
            className="flex items-center gap-1.5 bg-studio-card hover:bg-studio-border text-emerald-300 text-xs font-semibold px-3 py-2 rounded-xl transition border border-emerald-500/30 shadow-sm"
            title="Cấu hình VoiceStudio & Lồng tiếng AI"
          >
            <Sliders className="w-3.5 h-3.5 text-emerald-400" />
            <span>⚙️ VoiceStudio</span>
            <span className={`w-2 h-2 rounded-full ${voiceStudioOnline ? 'bg-emerald-400' : 'bg-amber-400'}`} />
          </button>

          <button
            onClick={handleSaveProject}
            disabled={isSaving}
            className="flex items-center gap-1.5 bg-studio-card hover:bg-studio-border text-gray-200 text-xs font-semibold px-3.5 py-2 rounded-xl transition border border-studio-border"
          >
            <Save className="w-3.5 h-3.5" />
            <span>{isSaving ? 'Đang lưu...' : 'Lưu Dự Án'}</span>
          </button>

          <button
            onClick={() => setShowRenderModal(true)}
            className="flex items-center gap-2 bg-gradient-to-r from-emerald-600 via-teal-600 to-indigo-600 hover:from-emerald-500 hover:to-indigo-500 text-white text-xs font-bold px-4 py-2 rounded-xl shadow-lg transition hover:scale-105 border border-emerald-400/40"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>Kết Xuất MP4 (HyperFrames)</span>
          </button>
        </div>
      </header>

      {/* Main Studio Workspace */}
      <main className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 p-6 max-w-[1780px] w-full mx-auto">
        {/* Left Column (4 cols): Research, Script, Genre, Voice & Affiliate Settings */}
        <section className="lg:col-span-4 flex flex-col gap-4 overflow-y-auto max-h-[calc(100vh-100px)] pr-1">
          {/* AI Deep Research Engine Card */}
          <div className="bg-studio-surface border border-studio-border rounded-2xl p-4 shadow-xl flex flex-col gap-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-white flex items-center gap-1.5">
                <Search className="w-4 h-4 text-studio-accent" />
                Nghiên Cứu Chủ Đề AI (Deep Research)
              </span>
              <button
                type="button"
                onClick={() => setShowResearchCard(!showResearchCard)}
                className="text-gray-400 hover:text-white text-xs flex items-center gap-1"
              >
                {showResearchCard ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              </button>
            </div>

            <div className="flex gap-2">
              <input
                type="text"
                value={topicQuery}
                onChange={(e) => setTopicQuery(e.target.value)}
                placeholder="Nhập chủ đề cần nghiên cứu (vd: Chiến dịch Điện Biên Phủ, Vàng và Lạm phát)..."
                className="flex-1 bg-studio-bg border border-studio-border rounded-xl px-3 py-2 text-xs text-gray-200 focus:outline-none focus:border-studio-primary font-medium"
              />
              <button
                type="button"
                onClick={handleResearchTopic}
                disabled={isResearching}
                className="px-3 py-2 bg-studio-accent/20 hover:bg-studio-accent/30 border border-studio-accent/40 text-studio-accent text-xs font-bold rounded-xl flex items-center gap-1.5 transition"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>{isResearching ? 'Đang tra cứu...' : 'Nghiên cứu'}</span>
              </button>
            </div>

            {/* Research Results Display */}
            {researchReport && (
              <div className="bg-studio-bg border border-studio-border/70 rounded-xl p-3 flex flex-col gap-2.5 text-xs">
                <div className="flex items-center justify-between border-b border-studio-border/50 pb-1.5">
                  <span className="font-semibold text-emerald-400 flex items-center gap-1">
                    <Check className="w-3.5 h-3.5" /> Nguồn kiểm chứng & Thực thể
                  </span>
                  <button
                    type="button"
                    onClick={handleApplyResearchToScript}
                    className="text-[11px] bg-studio-primary/20 text-studio-primary border border-studio-primary/30 px-2 py-0.5 rounded-md hover:bg-studio-primary hover:text-white transition"
                  >
                    Áp dụng vào Kịch Bản
                  </button>
                </div>

                {/* Facts with URLs */}
                <div className="space-y-1.5">
                  <div className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">Sự kiện xác thực:</div>
                  {(researchReport.verified_facts || []).map((fact: any, fIdx: number) => (
                    <div key={fIdx} className="bg-studio-card/80 p-2 rounded-lg text-gray-300 text-[11px] leading-relaxed">
                      <div className="font-medium text-white">{fact.claim}</div>
                      {fact.source_url && (
                        <a
                          href={fact.source_url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-studio-primary hover:underline flex items-center gap-1 mt-1 text-[10px]"
                        >
                          <ExternalLink className="w-2.5 h-2.5" /> {fact.source_name || 'Nguồn kiểm chứng'}
                        </a>
                      )}
                    </div>
                  ))}
                </div>

                {/* Narrative Strategy Hook */}
                {researchReport.narrative_strategy && (
                  <div className="bg-amber-950/20 border border-amber-600/30 p-2 rounded-lg text-[11px] text-amber-200">
                    <span className="font-bold">Mở đầu thu hút (Hook): </span>
                    {researchReport.narrative_strategy.hook_angle}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Format & Genre Selection Card */}
          <div className="bg-studio-surface border border-studio-border rounded-2xl p-4 shadow-xl flex flex-col gap-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-gray-300 flex items-center gap-1.5">
                <Layers className="w-4 h-4 text-studio-primary" />
                Định Dạng & Thể Loại
              </span>
              <div className="flex bg-studio-bg p-1 rounded-xl border border-studio-border text-xs">
                <button
                  onClick={() => handleFormatChange('short-form')}
                  className={`px-3 py-1 rounded-lg font-semibold transition ${
                    videoFormat === 'short-form' ? 'bg-studio-primary text-white' : 'text-gray-400 hover:text-white'
                  }`}
                >
                  Shorts (9:16)
                </button>
                <button
                  onClick={() => handleFormatChange('long-form')}
                  className={`px-3 py-1 rounded-lg font-semibold transition ${
                    videoFormat === 'long-form' ? 'bg-studio-primary text-white' : 'text-gray-400 hover:text-white'
                  }`}
                >
                  Long-form (16:9)
                </button>
              </div>
            </div>

            {/* 10 Genres Dropdown */}
            <div>
              <label className="block text-[11px] font-semibold text-gray-400 mb-1 flex items-center gap-1">
                <BookOpen className="w-3 h-3 text-studio-accent" /> Thể loại thông minh (Genre Intelligence):
              </label>
              <select
                value={selectedGenre}
                onChange={(e) => setSelectedGenre(e.target.value)}
                className="w-full bg-studio-bg border border-studio-border rounded-xl px-3 py-2 text-xs text-gray-200 focus:outline-none focus:border-studio-primary font-medium"
              >
                {genres.map(g => (
                  <option key={g.genre_id} value={g.genre_id}>
                    {g.display_name}
                  </option>
                ))}
              </select>
              {currentGenreObj && (
                <p className="text-[11px] text-gray-400 mt-1 italic leading-tight">
                  {currentGenreObj.description}
                </p>
              )}
            </div>

            {/* Video Duration Preset Selector */}
            <div className="pt-1 border-t border-studio-border/60">
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-[11px] font-semibold text-gray-300 flex items-center gap-1">
                  <Film className="w-3 h-3 text-studio-primary" /> Thời lượng mục tiêu:
                </label>
                <span className="text-[11px] font-mono text-emerald-400 font-bold bg-emerald-500/10 border border-emerald-500/30 px-2 py-0.5 rounded-md">
                  {targetDurationSec >= 60
                    ? `${Math.floor(targetDurationSec / 60)} phút${targetDurationSec % 60 ? ` ${targetDurationSec % 60}s` : ''}`
                    : `${targetDurationSec} giây`}
                </span>
              </div>
              <div className="grid grid-cols-4 gap-1.5">
                {videoFormat === 'short-form' ? (
                  <>
                    {[
                      { sec: 15, label: '15s', badge: 'Fast' },
                      { sec: 30, label: '30s', badge: 'Reels' },
                      { sec: 60, label: '60s', badge: 'Chuẩn' },
                      { sec: 90, label: '90s', badge: 'Dài' },
                    ].map((opt) => (
                      <button
                        key={opt.sec}
                        type="button"
                        onClick={() => setTargetDurationSec(opt.sec)}
                        className={`py-1.5 px-1 rounded-xl text-center transition border ${
                          targetDurationSec === opt.sec
                            ? 'bg-studio-primary border-studio-primary text-white shadow-md'
                            : 'bg-studio-bg border-studio-border text-gray-300 hover:text-white hover:border-gray-500'
                        }`}
                      >
                        <div className="text-xs font-bold">{opt.label}</div>
                        <div className="text-[9px] opacity-80">{opt.badge}</div>
                      </button>
                    ))}
                  </>
                ) : (
                  <>
                    {[
                      { sec: 120, label: '2 Phút', badge: 'Khám phá' },
                      { sec: 180, label: '3 Phút', badge: 'Cơ bản' },
                      { sec: 300, label: '5 Phút', badge: 'Chuyên sâu' },
                      { sec: 600, label: '10 Phút', badge: 'Đầy đủ' },
                    ].map((opt) => (
                      <button
                        key={opt.sec}
                        type="button"
                        onClick={() => setTargetDurationSec(opt.sec)}
                        className={`py-1.5 px-1 rounded-xl text-center transition border ${
                          targetDurationSec === opt.sec
                            ? 'bg-studio-primary border-studio-primary text-white shadow-md'
                            : 'bg-studio-bg border-studio-border text-gray-300 hover:text-white hover:border-gray-500'
                        }`}
                      >
                        <div className="text-xs font-bold">{opt.label}</div>
                        <div className="text-[9px] opacity-80">{opt.badge}</div>
                      </button>
                    ))}
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Script Input Card */}
          <div className="bg-studio-surface border border-studio-border rounded-2xl p-4 shadow-xl flex flex-col gap-3">
            <div className="flex items-center justify-between">
              <h2 className="text-xs font-bold text-white flex items-center gap-2">
                <Sliders className="w-4 h-4 text-studio-primary" />
                Nội Dung Kịch Bản
              </h2>
              <div className="text-[11px] text-gray-400 font-mono">
                {wordCount} từ • ~{estimatedDurationSec}s
              </div>
            </div>

            <textarea
              rows={8}
              value={scriptText}
              onChange={(e) => setScriptText(e.target.value)}
              placeholder="Nhập hoặc dán nội dung kịch bản video tiếng Việt tại đây..."
              className="w-full bg-studio-bg border border-studio-border rounded-xl p-3 text-xs text-gray-100 placeholder-gray-500 focus:outline-none focus:border-studio-primary transition resize-none leading-relaxed"
            />

            {/* Voice & Pacing Control */}
            <div className="grid grid-cols-2 gap-3 pt-1">
              <div>
                <label className="block text-[11px] font-semibold text-gray-400 mb-1 flex items-center gap-1">
                  <Mic className="w-3 h-3 text-studio-accent" /> Giọng đọc Edge-TTS:
                </label>
                <select
                  value={voiceVoice}
                  onChange={(e) => setVoiceVoice(e.target.value)}
                  className="w-full bg-studio-bg border border-studio-border rounded-lg px-2.5 py-1.5 text-xs text-gray-200 focus:outline-none focus:border-studio-primary"
                >
                  {voices.map(v => (
                    <option key={v.id} value={v.id}>{v.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-gray-400 mb-1 flex items-center gap-1">
                  <Volume2 className="w-3 h-3 text-studio-accent" /> Tốc độ nhịp:
                </label>
                <select
                  value={voiceRate}
                  onChange={(e) => setVoiceRate(e.target.value)}
                  className="w-full bg-studio-bg border border-studio-border rounded-lg px-2.5 py-1.5 text-xs text-gray-200 focus:outline-none focus:border-studio-primary"
                >
                  <option value="-15%">Chậm rãi (-15%)</option>
                  <option value="+0%">Tiêu chuẩn (+0%)</option>
                  <option value="+15%">Nhanh / Cuốn (+15%)</option>
                </select>
              </div>
            </div>

            {/* Action Buttons: Preview Voice & Analyze Script */}
            <div className="flex gap-2 pt-1">
              <button
                type="button"
                onClick={handleTestVoice}
                disabled={isVoiceTesting}
                className="flex-1 py-2 bg-studio-card hover:bg-studio-border border border-studio-border text-gray-200 text-xs font-semibold rounded-xl flex items-center justify-center gap-1.5 transition"
              >
                <Headphones className="w-3.5 h-3.5 text-studio-accent" />
                <span>{isVoiceTesting ? 'Đang phát...' : 'Nghe Thử Giọng'}</span>
              </button>

              <button
                type="button"
                onClick={handleGenerateVoiceForScenes}
                disabled={isSynthesizingVoice}
                className="flex-1 py-2 bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-500/40 text-emerald-300 text-xs font-bold rounded-xl flex items-center justify-center gap-1.5 transition"
              >
                <Music className="w-3.5 h-3.5" />
                <span>{isSynthesizingVoice ? 'Đang lồng tiếng...' : 'Lồng Tiếng Các Cảnh'}</span>
              </button>
            </div>

            <button
              type="button"
              onClick={handleAutoDiscoverAssets}
              disabled={isDiscoveringAssets}
              className="w-full py-2 bg-amber-600/20 hover:bg-amber-600/30 border border-amber-500/40 text-amber-300 text-xs font-bold rounded-xl flex items-center justify-center gap-1.5 transition"
            >
              <ImageIcon className="w-3.5 h-3.5" />
              <span>{isDiscoveringAssets ? 'Đang tìm & tải tư liệu hoạt họa...' : 'Tự Động Ghép Tư Liệu Hoạt Họa (100% Vector/Toon)'}</span>
            </button>

            {/* Zero-Touch 100% Automated Movie Creation */}
            <button
              type="button"
              onClick={handleZeroTouchGenerateMovie}
              disabled={isGeneratingMovie}
              className="w-full py-3.5 bg-gradient-to-r from-emerald-600 via-teal-600 to-indigo-600 hover:from-emerald-500 hover:to-indigo-500 disabled:opacity-50 text-white font-extrabold rounded-xl shadow-xl flex items-center justify-center gap-2 transition hover:scale-[1.01] mt-1 text-xs border border-emerald-400/40"
            >
              <Sparkles className="w-4 h-4 text-amber-300 animate-pulse" />
              <span>
                {isGeneratingMovie
                  ? 'Đang đạo diễn, lồng tiếng, tìm tư liệu & dựng phim tự động...'
                  : '🎬 Tạo Phim Tự Động 100% (Zero-Touch AI Studio)'}
              </span>
            </button>

            <button
              onClick={handleAnalyzeScript}
              disabled={isAnalyzing}
              className="w-full py-2.5 bg-studio-card hover:bg-studio-border border border-studio-border disabled:opacity-50 text-gray-300 font-semibold rounded-xl shadow flex items-center justify-center gap-2 transition hover:scale-[1.01] text-xs"
            >
              <Sparkles className="w-4 h-4 text-studio-highlight" />
              <span>{isAnalyzing ? 'Đang phân tích kịch bản theo thể loại...' : 'Phân Tích Kịch Bản Bằng AI'}</span>
            </button>
          </div>
        </section>

        {/* Middle Column (5 cols): Storyboard, Chapters & Scenes */}
        <section className="lg:col-span-5 flex flex-col gap-4 overflow-y-auto max-h-[calc(100vh-100px)] pr-1">
          {manifest.chapters && manifest.chapters.length > 1 && (
            <div className="bg-studio-surface border border-studio-border rounded-2xl p-4 shadow-xl">
              <h3 className="text-xs font-bold text-white mb-2 flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-studio-primary" />
                Cấu Trúc Chương (Long-Form Chapter Outline)
              </h3>
              <div className="flex flex-col gap-2">
                {manifest.chapters.map((ch, idx) => (
                  <div key={idx} className="bg-studio-bg border border-studio-border/70 rounded-xl p-2.5 flex items-start justify-between">
                    <div>
                      <div className="text-xs font-semibold text-gray-200">{ch.title}</div>
                      <div className="text-[11px] text-gray-400">{ch.summary}</div>
                    </div>
                    <span className="text-[10px] bg-studio-primary/20 text-studio-primary border border-studio-primary/30 px-2 py-0.5 rounded-full font-mono">
                      ~{Math.round(ch.estimated_duration_seconds)}s • {ch.scene_count} cảnh
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* DaVinci / CapCut Mode Switcher Tabs */}
          <div className="flex items-center justify-between bg-studio-surface border border-studio-border p-1.5 rounded-xl shadow">
            <div className="flex items-center gap-1">
              <button
                type="button"
                onClick={() => setEditorMode('timeline')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition ${
                  editorMode === 'timeline'
                    ? 'bg-studio-primary text-white shadow'
                    : 'text-gray-400 hover:text-white hover:bg-studio-card'
                }`}
              >
                <Sliders className="w-3.5 h-3.5" />
                <span>Timeline DaVinci / CapCut</span>
              </button>

              <button
                type="button"
                onClick={() => setEditorMode('cards')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition ${
                  editorMode === 'cards'
                    ? 'bg-studio-primary text-white shadow'
                    : 'text-gray-400 hover:text-white hover:bg-studio-card'
                }`}
              >
                <Layers className="w-3.5 h-3.5" />
                <span>Danh Sách Thẻ (Cards)</span>
              </button>
            </div>

            <span className="text-[10px] text-gray-400 font-mono pr-2">
              Thời lượng: {Math.round(manifest.total_duration_sec)}s
            </span>
          </div>

          {editorMode === 'timeline' ? (
            <TimelineEditor
              manifest={manifest}
              onChange={(m) => setManifest(m)}
              activeSceneIndex={activeSceneIndex}
              onSelectScene={(idx) => {
                setActiveSceneIndex(idx);
              }}
              currentTimeSec={currentTimeSec}
              onSeekTime={(t) => setCurrentTimeSec(t)}
            />
          ) : (
            <StoryboardEditor
              manifest={manifest}
              onChange={(m) => setManifest(m)}
              onSelectScene={(idx) => {
                setActiveSceneIndex(idx);
                const startSec = manifest.scenes.slice(0, idx).reduce((a, s) => a + s.duration_seconds, 0);
                setCurrentTimeSec(startSec);
              }}
              activeSceneIndex={activeSceneIndex}
            />
          )}
        </section>

        {/* Right Column (3 cols): Real-Time Canvas Player */}
        <section className="lg:col-span-3 flex flex-col items-center gap-4">
          <div className="bg-studio-surface border border-studio-border rounded-2xl p-4 shadow-xl w-full flex flex-col items-center">
            <h3 className="text-xs font-bold text-gray-300 uppercase tracking-wider mb-3">
              Xem Trước Khung Hình ({manifest.aspect_ratio})
            </h3>

            {/* Player Canvas */}
            <div className={`w-full ${manifest.video_format === 'long-form' ? 'aspect-[16/9] max-w-[340px]' : 'aspect-[9/16] max-w-[260px]'} rounded-xl overflow-hidden shadow-2xl border border-studio-border relative bg-black`}>
              <RemotionPlayer
                manifest={manifest}
                currentTimeSec={currentTimeSec}
                onTimeUpdate={(t) => setCurrentTimeSec(t)}
              />
            </div>

            <div className="w-full mt-4 flex flex-col gap-2">
              <button
                onClick={() => setShowRenderModal(true)}
                className="w-full py-2.5 bg-gradient-to-r from-emerald-600 to-indigo-600 hover:from-emerald-500 hover:to-indigo-500 text-white font-bold rounded-xl shadow text-xs flex items-center justify-center gap-1.5 transition"
              >
                <Play className="w-3.5 h-3.5 fill-current" />
                Kết Xuất Video MP4 (HyperFrames Engine)
              </button>
            </div>
          </div>
        </section>
      </main>

      {/* Render Modal */}
      <RenderModal
        manifest={manifest}
        isOpen={showRenderModal}
        onClose={() => {
          setShowRenderModal(false);
          setActiveJobId(null);
        }}
        initialJobId={activeJobId}
      />

      {/* VoiceStudio & TTS Configuration Modal */}
      {showVoiceStudioModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="bg-studio-surface border border-studio-border rounded-2xl max-w-xl w-full p-6 shadow-2xl flex flex-col gap-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-studio-border pb-3">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Sliders className="w-5 h-5 text-emerald-400" />
                  Cấu Hình VoiceStudio & Công Cụ Lồng Tiếng AI
                </h3>
                <p className="text-xs text-gray-400">Tích hợp thông minh bộ máy lồng tiếng nơ-ron miễn phí (debpalash/VoiceStudio)</p>
              </div>
              <button
                onClick={() => setShowVoiceStudioModal(false)}
                className="text-gray-400 hover:text-white p-1 text-sm font-bold"
              >
                ✕
              </button>
            </div>

            {/* Live Connection Status Badge */}
            <div className={`p-3.5 rounded-xl border flex items-center justify-between ${
              voiceStudioOnline
                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                : 'bg-amber-500/10 border-amber-500/30 text-amber-300'
            }`}>
              <div className="flex items-center gap-2.5">
                <span className={`w-3 h-3 rounded-full animate-pulse ${voiceStudioOnline ? 'bg-emerald-400' : 'bg-amber-400'}`} />
                <div>
                  <h4 className="text-xs font-bold">
                    {voiceStudioOnline ? 'VoiceStudio Đang Hoạt Động Trực Tuyến (Port 3900)' : 'VoiceStudio Chưa Chạy Cục Bộ'}
                  </h4>
                  <p className="text-[11px] opacity-80">
                    {voiceStudioOnline
                      ? 'Hệ thống đang ưu tiên tổng hợp giọng đọc nơ-ron qua VoiceStudio cục bộ.'
                      : 'Hệ thống đang tự động chuyển tiếp mượt mà sang Microsoft Edge Neural TTS ($0).'}
                  </p>
                </div>
              </div>
              <button
                onClick={handleCheckVoiceStudio}
                disabled={isCheckingVS}
                className="px-3 py-1.5 bg-studio-bg hover:bg-studio-border border border-studio-border rounded-lg text-xs font-semibold text-white transition flex-shrink-0"
              >
                {isCheckingVS ? 'Đang ping...' : 'Kiểm tra ping'}
              </button>
            </div>

            {/* Engine Selection Mode */}
            <div className="flex flex-col gap-2">
              <label className="text-xs font-bold text-gray-200">Chế độ ưu tiên bộ máy tạo giọng (Engine Routing):</label>
              <div className="grid grid-cols-1 gap-2">
                {[
                  {
                    id: 'auto',
                    title: '🚀 Tự động thông minh (Khuyên dùng)',
                    desc: 'Ưu tiên VoiceStudio cục bộ nếu đang bật; tự động chuyển sang Edge-TTS nếu VoiceStudio tắt.'
                  },
                  {
                    id: 'voicestudio',
                    title: '🎙️ Chỉ VoiceStudio (debpalash/VoiceStudio)',
                    desc: 'Bắt buộc chạy trên server VoiceStudio nội bộ trên máy bạn.'
                  },
                  {
                    id: 'edgetts',
                    title: '🌐 Trực tiếp Edge-TTS (Không cần cài thêm gì)',
                    desc: 'Sử dụng trực tiếp giọng đọc nơ-ron Nam Minh / Hoài My tốc độ cao.'
                  }
                ].map(mode => (
                  <label
                    key={mode.id}
                    onClick={() => setEngineMode(mode.id as any)}
                    className={`p-3 rounded-xl border cursor-pointer transition flex items-start gap-3 ${
                      engineMode === mode.id
                        ? 'bg-studio-primary/10 border-studio-primary text-white'
                        : 'bg-studio-bg border-studio-border text-gray-300 hover:border-gray-600'
                    }`}
                  >
                    <input
                      type="radio"
                      name="engine_mode"
                      checked={engineMode === mode.id}
                      onChange={() => setEngineMode(mode.id as any)}
                      className="mt-1"
                    />
                    <div>
                      <h5 className="text-xs font-bold text-white">{mode.title}</h5>
                      <p className="text-[11px] text-gray-400 mt-0.5">{mode.desc}</p>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* VoiceStudio Endpoint URL */}
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-bold text-gray-200">Địa chỉ VoiceStudio Server (HTTP Endpoint):</label>
              <input
                type="text"
                value={voiceStudioUrl}
                onChange={(e) => setVoiceStudioUrl(e.target.value)}
                placeholder="http://127.0.0.1:3900"
                className="bg-studio-bg border border-studio-border rounded-xl px-3.5 py-2 text-xs font-mono text-emerald-300 focus:outline-none focus:border-studio-primary"
              />
            </div>

            {/* Step-by-Step Launch Guide */}
            <div className="bg-studio-bg border border-studio-border rounded-xl p-3 flex flex-col gap-2">
              <span className="text-[11px] font-bold text-gray-300 flex items-center gap-1.5">
                📖 Lệnh khởi chạy debpalash/VoiceStudio (nếu muốn chạy cục bộ):
              </span>
              <pre className="bg-black/50 p-2.5 rounded-lg text-[10px] font-mono text-amber-300 overflow-x-auto border border-studio-border/50">
git clone https://github.com/debpalash/VoiceStudio.git && cd VoiceStudio && python -m voicestudio --port 3900
              </pre>
            </div>

            {/* Modal Actions */}
            <div className="flex items-center justify-end gap-2 pt-2 border-t border-studio-border">
              <button
                onClick={() => setShowVoiceStudioModal(false)}
                className="px-4 py-2 bg-studio-card hover:bg-studio-border text-gray-300 text-xs font-semibold rounded-xl transition"
              >
                Đóng
              </button>
              <button
                onClick={handleSaveVoiceStudioSettings}
                className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-xl transition shadow"
              >
                Lưu Cấu Hình
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
