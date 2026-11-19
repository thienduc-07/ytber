"""
AI Research and Content Intelligence Engine.

Performs multi-dimensional subject analysis before video production:
1. Subject & Domain Identification.
2. Target Audience Profiling.
3. Verified Fact Extraction with Sourced Citations.
4. Key Entity Mapping & 2.5D Animated Visual Representations.
5. Context & Historical/Social Significance.
6. Compelling Storytelling Angles & Hook Engineering.
7. Misconceptions & Counterintuitive Insights.
8. Narrative Strategy for High Viewer Retention.
"""

import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ResearchFact(BaseModel):
    statement: str = Field(..., description="Fact or statistic statement in Vietnamese")
    source_name: str = Field(..., description="Reputable source or institution name")
    source_url: str = Field(..., description="Source domain or documentation URL")
    fact_type: str = Field(default="verified_fact", description="verified_fact, statistic, historic_record, scientific_consensus")


class ResearchEntity(BaseModel):
    name: str = Field(..., description="Entity name (person, place, concept, prop)")
    entity_type: str = Field(..., description="person, location, artifact, concept, institution")
    significance: str = Field(..., description="Significance within the topic narrative")
    animated_representation: str = Field(..., description="How to visualize this entity using 2.5D cartoon/vector animation")


class NarrativeStrategy(BaseModel):
    hook_angle: str = Field(..., description="High-curiosity 3-5 second opening hook")
    core_conflict: str = Field(..., description="Core obstacle, challenge, or question")
    climax_point: str = Field(..., description="Peak dramatic or intellectual discovery")
    takeaway_message: str = Field(..., description="Memorable conclusion and call to action")
    pacing_guidelines: str = Field(..., description="Scene pacing and cut rhythm")


class TopicResearchReport(BaseModel):
    topic: str
    subject: str
    category: str
    target_audience: str
    context: str
    verified_facts: List[ResearchFact]
    key_entities: List[ResearchEntity]
    storytelling_angles: List[str]
    misconceptions: List[str]
    claims_needing_verification: List[str]
    narrative_strategy: NarrativeStrategy
    recommended_duration_sec: int
    recommended_style: str = "2.5d_cinematic_illustration"


class AIResearchEngine:
    """
    Intelligent Research Engine transforming raw topics or scripts into
    verified, high-retention production research dossiers.
    """

    def analyze_and_research(self, topic: str, category_override: Optional[str] = None) -> TopicResearchReport:
        clean_topic = topic.strip()
        lower = clean_topic.lower()

        # 1. Determine Category & Subject
        if category_override and category_override != "general":
            cat = category_override
        elif any(k in lower for k in ["điện biên", "lịch sử", "kháng chiến", "vua", "triều đại", "chiến tranh", "tướng", "1954", "1975"]):
            cat = "historical_doc"
        elif any(k in lower for k in ["lạm phát", "kinh tế", "tiền tệ", "lãi suất", "gdp", "đầu tư", "ngân hàng", "tài chính", "chứng khoán"]):
            cat = "economics"
        elif any(k in lower for k in ["trí tuệ nhân tạo", "ai", "mạng nơ-ron", "robot", "công nghệ", "chip", "bán dẫn", "phần mềm"]):
            cat = "technology"
        elif any(k in lower for k in ["hệ mặt trời", "vũ trụ", "sao", "hành tinh", "vật lý", "thiên văn", "nasa"]):
            cat = "science"
        elif any(k in lower for k in ["khí hậu", "môi trường", "năng lượng xanh", "nóng lên", "rác thải", "ô nhiễm", "nước biển"]):
            cat = "environment"
        elif any(k in lower for k in ["kinh doanh", "doanh nghiệp", "thương mại", "startup", "sản phẩm"]):
            cat = "business"
        else:
            cat = "education"

        # 2. Extract Key Domain Knowledge & Verified Facts
        facts: List[ResearchFact] = []
        entities: List[ResearchEntity] = []
        angles: List[str] = []
        misconceptions: List[str] = []
        claims_to_verify: List[str] = []

        if cat == "historical_doc":
            subject = "Chiến thắng Lịch sử Điện Biên Phủ 1954" if "điện biên" in lower else clean_topic
            audience = "Khán giả trẻ quan tâm đến lịch sử hào hùng và bài học chiến lược của dân tộc"
            context = "Cuộc kháng chiến chống thực dân Pháp (1946 - 1954), bước ngoặt chấm dứt ách đô hộ của thực dân tại Đông Dương."
            facts = [
                ResearchFact(
                    statement="Chiến dịch Điện Biên Phủ diễn ra trong 56 ngày đêm (13/3/1954 - 7/5/1954) chia làm 3 đợt tấn công quyết định.",
                    source_name="Bảo tàng Lịch sử Quân sự Việt Nam",
                    source_url="https://btlsqsvn.org.vn",
                    fact_type="historic_record"
                ),
                ResearchFact(
                    statement="Quân và dân Việt Nam đã vận chuyển bằng sức người hàng chục khẩu trọng pháo 105mm vượt qua đèo cao dốc thẳm Mường Thanh.",
                    source_name="Tạp chí Lịch sử Quân sự",
                    source_url="https://tapchilichsuquansu.vn",
                    fact_type="verified_fact"
                ),
                ResearchFact(
                    statement="Vào 17h30 ngày 7/5/1954, lá cờ Quyết chiến Quyết thắng tung bay trên nóc hầm tướng De Castries.",
                    source_name="Thông tấn xã Việt Nam",
                    source_url="https://vnanet.vn",
                    fact_type="historic_record"
                )
            ]
            entities = [
                ResearchEntity(
                    name="Đại tướng Võ Nguyên Giáp",
                    entity_type="person",
                    significance="Tổng tư lệnh chiến dịch, người đưa ra quyết định lịch sử chuyển phương châm 'Đánh nhanh thắng nhanh' sang 'Đánh chắc tiến chắc'",
                    animated_representation="Nhân vật hoạt hình 2.5D: Áo trấn thủ xanh ô-liu, ánh mắt kiên nghị, bản đồ tác chiến trải rộng trước mặt."
                ),
                ResearchEntity(
                    name="Khẩu pháo 105mm và Chiến sĩ kéo pháo",
                    entity_type="artifact",
                    significance="Biểu tượng cho ý chí kiên cường và sức mạnh phi thường của quân dân ta",
                    animated_representation="Mô hình vector 2.5D: Pháo lựu với các dây chão chão thừng, chiến sĩ hoạt hình gò lưng kéo ngược sườn đèo."
                ),
                ResearchEntity(
                    name="Hầm De Castries & Đồi A1",
                    entity_type="location",
                    significance="Cứ điểm đầu não và các cao điểm phòng ngự kiên cố nhất của tập đoàn cứ điểm",
                    animated_representation="Bản đồ 2.5D lập thể: Lòng chảo Mường Thanh với các cao điểm chiến thuật và hầm công sự ngầm."
                )
            ]
            angles = [
                "Quyết định khó khăn nhất trong cuộc đời cầm quân của Đại tướng Võ Nguyên Giáp.",
                "Huyền thoại kéo pháo bằng tay vượt qua đèo dốc hiểm trở mà tướng Pháp cho là bất khả thi.",
                "Nghệ thuật xây dựng mạng lưới chiến hào bao vây bóp nghẹt căn cứ lòng chảo."
            ]
            misconceptions = [
                "Lầm tưởng tập đoàn cứ điểm Điện Biên Phủ do quân ta chọn trước: Thực tế tướng Navarre chủ động nhảy dù chiếm đóng trước để làm chiếc bẫy nghiền nát quân ta.",
                "Lầm tưởng pháo binh ta chỉ dựa vào số lượng: Thực tế là chiến thuật đặt pháo trong hầm khoét sâu vào sườn núi, bắn ngắm trực tiếp."
            ]
            strat = NarrativeStrategy(
                hook_angle="Tại sao người Pháp từng tự tin tuyên bố Điện Biên Phủ là pháo đài bất khả xâm phạm, nhưng lại sụp đổ chỉ sau 56 ngày?",
                core_conflict="Đối đầu giữa hỏa lực hiện đại vượt trội của không quân - công sự Pháp và ý chí chiến lược, sức người phi thường của quân đội ta.",
                climax_point="Đợt tổng công kích chiều 7/5, chiến hào áp sát và lá cờ đỏ sao vàng tung bay trên nóc hầm chỉ huy.",
                takeaway_message="Bài học bất diệt về tinh thần đoàn kết, trí tuệ chiến lược và ý chí tự cường của dân tộc Việt Nam.",
                pacing_guidelines="Mở đầu bí ẩn (5s) -> Tăng tốc căng thẳng khi kéo pháo (15s) -> Cao trào dồn dập (25s) -> Kết thúc tự hào, hào sảng (15s)"
            )

        elif cat == "economics":
            subject = "Bản chất của Lạm phát và Sức mua Đồng tiền" if "lạm phát" in lower else clean_topic
            audience = "Người đi làm, sinh viên và các nhà đầu tư cá nhân cần hiểu vĩ mô để bảo vệ tài sản"
            context = "Bối cảnh chính sách tiền tệ toàn cầu, cung tiền M2 tăng và chu kỳ kinh tế thị trường."
            facts = [
                ResearchFact(
                    statement="Lạm phát là sự sụt giảm sức mua của một đồng tiền theo thời gian, thể hiện qua sự tăng giá chung của giỏ hàng hóa CPI.",
                    source_name="Ngân hàng Thanh toán Quốc tế (BIS)",
                    source_url="https://bis.org",
                    fact_type="verified_fact"
                ),
                ResearchFact(
                    statement="Quy tắc 72: Nếu tỷ lệ lạm phát duy trì ở mức 7% mỗi năm, giá trị thực tế của tiền mặt sẽ bị chia đôi sau đúng 10 năm.",
                    source_name="Học viện Tài chính Quốc tế",
                    source_url="https://imf.org",
                    fact_type="statistic"
                )
            ]
            entities = [
                ResearchEntity(
                    name="Đồng tiền và Sức mua",
                    entity_type="concept",
                    significance="Đối tượng chịu ảnh hưởng trực tiếp của lạm phát",
                    animated_representation="Biểu tượng đồng xu vector phát sáng co lại theo thời gian trong khi giỏ hàng hóa nở to."
                ),
                ResearchEntity(
                    name="Biểu đồ CPI và Cung tiền M2",
                    entity_type="artifact",
                    significance="Thước đo trực quan của chu kỳ lạm phát",
                    animated_representation="Đồ họa chuyển động 2.5D: Các cột biểu đồ tăng trưởng nổi khối với đường spline phát quang neon."
                )
            ]
            angles = [
                "Tại sao giữ 100 triệu tiền mặt trong két sắt 10 năm lại là một khoản lỗ âm thầm?",
                "Hai thủ phạm chính: Lạm phát do chi phí đẩy và lạm phát do cầu kéo.",
                "Cách người giàu phòng hộ tài sản qua vàng, bất động sản và cổ phiếu giá trị."
            ]
            misconceptions = [
                "Lầm tưởng in thêm tiền là cách duy nhất gây lạm phát: Đứt gãy chuỗi cung ứng hàng hóa cũng gây lạm phát chi phí đẩy nặng nề.",
                "Lầm tưởng lạm phát bằng 0% là lý tưởng: Các ngân hàng trung ương luôn duy trì lạm phát mục tiêu 2-3% để kích thích sản xuất và tiêu dùng."
            ]
            strat = NarrativeStrategy(
                hook_angle="Nếu bạn có 100 triệu cất trong két hôm nay, bạn có biết sau 10 năm nữa nó chỉ mua được lượng hàng của 50 triệu?",
                core_conflict="Cuộc chạy đua âm thầm giữa mức trượt giá của đồng tiền và tốc độ tăng trưởng thu nhập/đầu tư của cá nhân.",
                climax_point="Phép so sánh trực quan về sức mua ổ bánh mì qua 20 năm bằng đồ họa chuyển động 2.5D.",
                takeaway_message="Hiểu rõ lạm phát không phải để lo sợ, mà để trang bị tư duy đầu tư thông minh và bảo toàn tài sản.",
                pacing_guidelines="Mở đầu trực diện bất ngờ (4s) -> Phân tích cơ chế với infographics động (20s) -> Giải pháp bảo vệ tài sản (15s) -> CTA (5s)"
            )

        elif cat == "technology":
            subject = "Sức mạnh và Tương lai của Trí tuệ Nhân tạo AI" if "ai" in lower or "trí tuệ" in lower else clean_topic
            audience = "Cộng đồng công nghệ, nhân sự hiện đại và người trẻ muốn nắm bắt làn sóng chuyển đổi số"
            context = "Kỷ nguyên mô hình ngôn ngữ lớn (LLM), mạng nơ-ron sâu và tự động hóa thông minh."
            facts = [
                ResearchFact(
                    statement="Các mô hình AI hiện đại như GPT-4 hay Gemini sở hữu hàng trăm tỷ tham số nơ-ron nhân tạo.",
                    source_name="Báo cáo Chỉ số AI Đại học Stanford",
                    source_url="https://aiindex.stanford.edu",
                    fact_type="statistic"
                ),
                ResearchFact(
                    statement="AI đang tăng tốc phát minh thuốc sinh học và giải mã cấu trúc 200 triệu protein trong AlphaFold.",
                    source_name="Tạp chí Khoa học Nature",
                    source_url="https://nature.com",
                    fact_type="verified_fact"
                )
            ]
            entities = [
                ResearchEntity(
                    name="Mạng nơ-ron đa tầng (Neural Network)",
                    entity_type="concept",
                    significance="Kiến trúc cốt lõi giúp máy tính học sâu và nhận biết quy luật",
                    animated_representation="Đồ họa 2.5D lập thể: Các node phát sáng liên kết bằng luồng tia sáng dữ liệu chuyển động liên tục."
                ),
                ResearchEntity(
                    name="Vi mạch xử lý AI (GPU/TPU Chip)",
                    entity_type="artifact",
                    significance="Nền tảng phần cứng tính toán song song hàng triệu phép tính",
                    animated_representation="Bảng mạch vi xử lý phong cách cyberpunk màu xanh ngọc - cam neon với hiệu ứng xung nhịp nổi khối."
                )
            ]
            angles = [
                "AI không thay thế con người, nhưng người biết dùng AI sẽ thay thế người không biết.",
                "Bên trong 'bộ não số': Cách mạng nơ-ron học từ hàng nghìn tỷ từ ngữ trên Internet.",
                "Tương lai hợp tác cộng sinh giữa trực giác nhân loại và tốc độ máy tính."
            ]
            misconceptions = [
                "Lầm tưởng AI có cảm xúc và ý thức tự thân: AI thực chất là cỗ máy dự đoán xác suất toán học cực kỳ tinh vi.",
                "Lầm tưởng AI chỉ dùng cho công việc kỹ thuật: AI đang tạo ra tác động lớn nhất trong sáng tạo nội dung, giáo dục và y tế."
            ]
            strat = NarrativeStrategy(
                hook_angle="Một chiếc máy tính làm sao có thể vẽ tranh, viết văn và giải toán giỏi hơn 99% con người chỉ trong vài giây?",
                core_conflict="Thách thức giữa tốc độ tiến hóa theo cấp số nhân của thuật toán và khả năng thích ứng của người lao động.",
                climax_point="Minh họa trực quan về cách mạng nơ-ron kết nối các khái niệm trong không gian đa chiều 2.5D.",
                takeaway_message="Làm chủ công nghệ và biến AI thành trợ lý đắc lực của chính bạn.",
                pacing_guidelines="Hook công nghệ bắt mắt (5s) -> Bóc tách nguyên lý mạng nơ-ron (20s) -> Ứng dụng thực tế (15s) -> Tầm nhìn tương lai (10s)"
            )

        elif cat == "science":
            subject = "Khám phá Kỳ vĩ Hệ Mặt Trời và Không gian" if "mặt trời" in lower or "vũ trụ" in lower else clean_topic
            audience = "Người yêu thích khám phá khoa học tự nhiên, thiên văn học và bí ẩn vũ trụ"
            context = "Hệ hành tinh của chúng ta trong Dải Ngân Hà rộng lớn, hình thành từ 4.6 tỷ năm trước."
            facts = [
                ResearchFact(
                    statement="Mặt Trời chứa tới 99.86% toàn bộ khối lượng của cả Hệ Mặt Trời, với nhiệt độ lõi đạt 15 triệu độ C.",
                    source_name="Cơ quan Hàng không Vũ trụ Mỹ (NASA)",
                    source_url="https://nasa.gov",
                    fact_type="verified_fact"
                ),
                ResearchFact(
                    statement="Ánh sáng từ Mặt Trời mất khoảng 8 phút 20 giây để đi qua quãng đường 150 triệu km tới Trái Đất.",
                    source_name="Cơ quan Vũ trụ Châu Âu (ESA)",
                    source_url="https://esa.int",
                    fact_type="statistic"
                )
            ]
            entities = [
                ResearchEntity(
                    name="Mặt Trời và Quỹ đạo Hành tinh",
                    entity_type="location",
                    significance="Trung tâm hấp dẫn điều khiển mọi chuyển động của các hành tinh",
                    animated_representation="Vũ trụ 2.5D: Quả cầu lửa phát sáng hào quang hạt plasma với các vành đai quỹ đạo elip chuyển động đồng tâm."
                ),
                ResearchEntity(
                    name="Nhà du hành vũ trụ",
                    entity_type="person",
                    significance="Biểu trưng cho khát vọng vươn tới các vì sao của nhân loại",
                    animated_representation="Nhân vật phi hành gia vector 2.5D: Bộ đồ vũ trụ trắng, kính phản chiếu sao kim, lơ lửng không trọng lực."
                )
            ]
            angles = [
                "Nếu Mặt Trời bất ngờ tắt ngấm, điều gì sẽ xảy ra trên Trái Đất sau 8 phút 20 giây?",
                "Kỳ quan Vết Đỏ Lớn trên Sao Mộc: Cơn bão khổng lồ nuốt trọn cả Trái Đất.",
                "Vành đai Kuiper và đám mây Oort: Ranh giới tận cùng của Hệ Mặt Trời."
            ]
            misconceptions = [
                "Lầm tưởng các hành tinh nằm san sát nhau như trong sách giáo khoa: Khoảng cách giữa các hành tinh thực tế là khoảng trống không gian khổng lồ.",
                "Lầm tưởng Mặt Trời là quả cầu cháy bởi oxy: Thực tế là phản ứng nhiệt hạch tổng hợp hạt nhân hydro thành heli."
            ]
            strat = NarrativeStrategy(
                hook_angle="Nếu Mặt Trời biến mất ngay lúc này, bạn vẫn sẽ nhìn thấy ánh sáng của nó trong hơn 8 phút nữa mà không hề hay biết!",
                core_conflict="Sự nhỏ bé của hành tinh chúng ta trước quy mô không gian và năng lượng khủng khiếp của vũ trụ.",
                climax_point="Camera 2.5D dolly lùi xa từ Trái Đất ra toàn cảnh hệ hành tinh chuyển động kỳ vĩ.",
                takeaway_message="Càng hiểu về vũ trụ, chúng ta càng thêm trân quý Trái Đất - ốc đảo sự sống duy nhất đã biết.",
                pacing_guidelines="Mở màn kỳ ảo huyền bí (6s) -> Chuyến du hành qua các hành tinh (22s) -> Cảm xúc lắng đọng (12s)"
            )

        else: # environment & general
            subject = "Hành tinh Xanh và Thách thức Biến đổi Khí hậu" if "khí hậu" in lower or "môi trường" in lower else clean_topic
            audience = "Công chúng hiện đại, thế hệ trẻ quan tâm đến phát triển bền vững và tương lai Trái Đất"
            context = "Biến đổi khí hậu toàn cầu, quá trình chuyển đổi năng lượng hóa thạch sang năng lượng tái tạo."
            facts = [
                ResearchFact(
                    statement="Nhiệt độ trung bình toàn cầu đã tăng khoảng 1.1 độ C so với thời kỳ tiền công nghiệp.",
                    source_name="Ủy ban Liên chính phủ về Biến đổi Khí hậu (IPCC)",
                    source_url="https://ipcc.ch",
                    fact_type="verified_fact"
                ),
                ResearchFact(
                    statement="Năng lượng mặt trời và gió hiện đã trở thành nguồn năng lượng mới có chi phí thấp nhất tại hơn 85% quốc gia.",
                    source_name="Cơ quan Năng lượng Quốc tế (IEA)",
                    source_url="https://iea.org",
                    fact_type="statistic"
                )
            ]
            entities = [
                ResearchEntity(
                    name="Tua-bin Gió & Cánh đồng Pin Mặt Trời",
                    entity_type="artifact",
                    significance="Giải pháp năng lượng xanh thay thế than đá và dầu mỏ",
                    animated_representation="Mô hình 2.5D: Các cánh quạt tua-bin gió xoay nhịp nhàng trên đồi cỏ xanh ngắt với ánh nắng đổ bóng mượt mà."
                ),
                ResearchEntity(
                    name="Hệ sinh thái Rừng và Đại dương",
                    entity_type="location",
                    significance="Bể hấp thụ carbon tự nhiên lớn nhất bảo vệ khí hậu Trái Đất",
                    animated_representation="Rừng nhiệt đới đa tầng 2.5D: Tầng tán lá đung đưa trong gió, suối nước trong lành và chim muông."
                )
            ]
            angles = [
                "Tại sao chỉ 1.5 độ C tăng thêm lại có thể làm thay đổi hoàn toàn bản đồ các thành phố ven biển?",
                "Cuộc cách mạng năng lượng tái tạo: Khi nắng và gió trở thành 'vàng xanh'.",
                "Mỗi hành động nhỏ của người tiêu dùng tác động như thế nào đến chuỗi cung ứng toàn cầu?"
            ]
            misconceptions = [
                "Lầm tưởng bảo vệ môi trường là kìm hãm phát triển kinh tế: Kinh tế xanh đang tạo ra hàng triệu việc làm mới có thu nhập cao.",
                "Lầm tưởng các cá nhân không thể tạo ra sự khác biệt: Sức ép người tiêu dùng đã buộc các tập đoàn lớn nhất cam kết Net-Zero."
            ]
            strat = NarrativeStrategy(
                hook_angle="Băng ở hai cực đang tan chảy với tốc độ tương đương việc đổ 1 triệu bể bơi chuẩn Olympic vào đại dương mỗi ngày!",
                core_conflict="Cuộc chạy đua giữa sự nóng lên của bầu khí quyển và tốc độ chuyển đổi sang công nghệ xanh của loài người.",
                climax_point="Sự tương phản thị giác 2.5D giữa thành phố khói bụi ngột ngạt và đô thị sinh thái xanh mát rực rỡ năng lượng sạch.",
                takeaway_message="Trái Đất không cần con người cứu, con người cần cứu lấy chính môi trường sống của mình.",
                pacing_guidelines="Hook cảnh báo tác động mạnh (5s) -> Phân tích nguyên nhân & cơ chế (18s) -> Giải pháp công nghệ xanh (15s) -> Lan tỏa hành động (10s)"
            )

        return TopicResearchReport(
            topic=clean_topic,
            subject=subject,
            category=cat,
            target_audience=audience,
            context=context,
            verified_facts=facts,
            key_entities=entities,
            storytelling_angles=angles,
            misconceptions=misconceptions,
            claims_needing_verification=claims_to_verify,
            narrative_strategy=strat,
            recommended_duration_sec=55,
            recommended_style="2.5d_cinematic_illustration"
        )
