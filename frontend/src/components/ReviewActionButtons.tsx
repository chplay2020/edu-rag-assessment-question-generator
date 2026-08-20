import React, { useState } from 'react';
import { reviewQuestion } from '../services/questionApi';
import { Check, X } from '@phosphor-icons/react';
import './ReviewActionButtons.css';

interface Props {
  questionId: number;
  currentStatus: string;
  onSuccess: () => void;
  isEn?: boolean;
}

export const ReviewActionButtons: React.FC<Props> = ({ questionId, currentStatus, onSuccess, isEn }) => {
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
      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
        <input 
          type="text" 
          placeholder={isEn ? `Reason to ${showConfirm === 'approved' ? 'approve' : 'reject'}...` : `Lý do ${showConfirm === 'approved' ? 'duyệt' : 'từ chối'}...`} 
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
          className="jr-form-select"
          style={{ width: '250px', padding: '6px 12px', height: '32px' }}
        />
        <button className="jr-btn-primary" onClick={handleAction} disabled={loading}>{isEn ? 'Confirm' : 'Xác nhận'}</button>
        <button className="jr-btn-secondary" onClick={() => setShowConfirm(null)} disabled={loading}>{isEn ? 'Cancel' : 'Hủy'}</button>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', gap: '8px' }}>
      <button 
        className="jr-btn-approve" 
        onClick={() => setShowConfirm('approved')}
        disabled={currentStatus === 'approved'}
      >
        <Check size={14} /> {isEn ? 'Approve' : 'Duyệt'}
      </button>
      <button 
        className="jr-btn-reject" 
        onClick={() => setShowConfirm('rejected')}
        disabled={currentStatus === 'rejected'}
      >
        <X size={14} /> {isEn ? 'Reject' : 'Từ chối'}
      </button>
    </div>
  );
};
