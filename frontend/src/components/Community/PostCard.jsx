import { useState } from 'react';
import './PostCard.css';

export default function PostCard({ post }) {
  const [liked, setLiked]   = useState(post.liked || false);
  const [likes, setLikes]   = useState(post.likes || 0);

  const toggleLike = () => {
    setLiked(prev => !prev);
    setLikes(prev => prev + (liked ? -1 : 1));
  };

  return (
    <div className="post-card">
      <div className="post-top">
        <div className="user-avatar">{post.avatar}</div>
        <div>
          <div className="username">{post.user}</div>
          <div className="post-time">{post.time}</div>
        </div>
      </div>

      <div className="post-img">{post.emoji}</div>

      <div className="post-body">
        <div className="post-place">📍 {post.place}</div>
        <p className="post-text">{post.text}</p>
        <div className="post-actions">
          <button className={`action-btn ${liked ? 'liked' : ''}`} onClick={toggleLike}>
            {liked ? '❤️' : '🤍'} {likes}
          </button>
          <button className="action-btn">💬 댓글</button>
          <button className="action-btn">🔗 공유</button>
        </div>
      </div>
    </div>
  );
}
