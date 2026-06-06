import PostCard from '../components/Community/PostCard';
import './CommunityPage.css';

// 실제 구현 시 백엔드 API에서 가져옴
const MOCK_POSTS = [
  { id:1, user:'초코아빠', avatar:'초', emoji:'🐕', place:'멍멍식탁, 수원 행궁동', text:'오늘 초코랑 멍멍식탁 다녀왔어요! 대형견도 완전 환영해줘서 너무 좋았습니다 🐾', likes:24, liked:false, time:'2시간 전' },
  { id:2, user:'벨라맘',   avatar:'벨', emoji:'🐩', place:'댕댕카페, 수원 화서문로', text:'벨라 생일 파티 🎂 댕댕카페에서 강아지 전용 케이크 사줬더니 넘 좋아하네요 ㅋㅋ', likes:41, liked:true,  time:'5시간 전' },
  { id:3, user:'콩이네',   avatar:'콩', emoji:'🦮', place:'반려동물 테마공원, 광교',  text:'광교 테마공원 처음 가봤는데 대형견 구역이 따로 있어서 안심이에요~ 콩이도 실컷 뛰었네요 ㅎㅎ', likes:18, liked:false, time:'어제' },
];

export default function CommunityPage() {
  return (
    <div className="community-page">
      <div className="comm-header">
        <span className="comm-title">🐾 반려동물 자랑 게시판</span>
        <button className="write-btn">+ 글쓰기</button>
      </div>
      <div className="posts-container">
        {MOCK_POSTS.map(post => <PostCard key={post.id} post={post} />)}
      </div>
    </div>
  );
}
