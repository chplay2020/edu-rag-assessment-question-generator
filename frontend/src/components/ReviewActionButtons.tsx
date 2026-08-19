import React, { useState } from 'react';
import { reviewQuestion } from '../services/questionApi';
import { Check, X } from '@phosphor-icons/react';
import './ReviewActionButtons.css';

interface Props {
  questionId: number;
  currentStatus: string;
  onSuccess: () => void;
}

export const ReviewActionButtons: React.FC<Props> = ({ questionId, currentStatus, onSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [showConfirm, setShowConfirm] = useState<'approved' | 'rejected' | null>(null);
  const [feedback, setFeedback] = useState('');

  const handleAction = async () => {
    if (!showConfirm) return;
    setLoading(true);
    try {
      await reviewQuestion(questionId, { status: showConfirm, feedback });
      setShowConfirm(null);
      setFeedback('');
      onSuccess();
    } catch (err) {
      console.error(err);
      alert('Có lỗi xảy ra khi duyệt câu hỏi');
    } finally {
      setLoading(false);
    }
  };

  if (showConfirm) {
    return (
      <div className="rab-confirm-box">
        <input 
          type="text" 
          placeholder={`Lý do ${showConfirm === 'approved' ? 'duyệt' : 'từ chối'}...`} 
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
          className="rab-input"
        />
        <button className="rab-btn rab-btn-primary" onClick={handleAction} disabled={loading}>Xác nhận</button>
        <button className="rab-btn rab-btn-secondary" onClick={() => setShowConfirm(null)} disabled={loading}>Hủy</button>
      </div>
    );
  }

  return (
    <div className="rab-actions">
      <button 
        className="rab-btn rab-btn-reject" 
        onClick={() => setShowConfirm('rejected')}
        disabled={currentStatus === 'rejected'}
      >
        <X size={16} /> Từ chối
      </button>
      <button 
        className="rab-btn rab-btn-approve" 
        onClick={() => setShowConfirm('approved')}
        disabled={currentStatus === 'approved'}
      >
        <Check size={16} /> Duyệt
      </button>
    </div>
  );
};
