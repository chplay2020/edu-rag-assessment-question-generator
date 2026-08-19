import React, { useState } from 'react';
import type { QuestionResponse, Option } from '../services/jobApi';
import { updateQuestion } from '../services/questionApi';
import { X, Plus, Trash } from '@phosphor-icons/react';
import './QuestionEditorModal.css';

interface Props {
  question: QuestionResponse;
  onClose: () => void;
  onSuccess: () => void;
}

export const QuestionEditorModal: React.FC<Props> = ({ question, onClose, onSuccess }) => {
  const [content, setContent] = useState(question.content);
  const [explanation, setExplanation] = useState(question.explanation || '');
  const [difficulty, setDifficulty] = useState(question.difficulty);
  const [bloomLevel, setBloomLevel] = useState(question.bloom_level);
  const [options, setOptions] = useState<Option[]>(JSON.parse(JSON.stringify(question.options)));
  const [loading, setLoading] = useState(false);

  const handleSave = async () => {
    setLoading(true);
    try {
      await updateQuestion(question.id, {
        content,
        explanation,
        difficulty,
        bloom_level: bloomLevel,
        options: options.map(o => ({ content: o.content, is_correct: o.is_correct }))
      });
      onSuccess();
    } catch (err) {
      console.error(err);
      alert('Có lỗi xảy ra khi lưu câu hỏi');
    } finally {
      setLoading(false);
    }
  };

  const updateOptionContent = (index: number, val: string) => {
    const newOptions = [...options];
    newOptions[index].content = val;
    setOptions(newOptions);
  };

  const setCorrectOption = (index: number) => {
    const newOptions = options.map((o, i) => ({
      ...o,
      is_correct: i === index
    }));
    setOptions(newOptions);
  };

  const removeOption = (index: number) => {
    setOptions(options.filter((_, i) => i !== index));
  };

  const addOption = () => {
    setOptions([...options, { id: 0, content: '', is_correct: false }]);
  };

  return (
    <div className="qem-overlay">
      <div className="qem-modal">
        <div className="qem-header">
          <h2>Chỉnh sửa câu hỏi</h2>
          <button className="qem-btn-close" onClick={onClose}><X size={24} /></button>
        </div>
        <div className="qem-body">
          <div className="qem-form-group">
            <label>Nội dung câu hỏi</label>
            <textarea value={content} onChange={(e) => setContent(e.target.value)} rows={4} />
          </div>
          
          <div className="qem-form-row">
            <div className="qem-form-group">
              <label>Độ khó</label>
              <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
                <option value="easy">Dễ</option>
                <option value="medium">Trung bình</option>
                <option value="hard">Khó</option>
              </select>
            </div>
            <div className="qem-form-group">
              <label>Mức độ Bloom</label>
              <select value={bloomLevel} onChange={(e) => setBloomLevel(e.target.value)}>
                <option value="Remember">Remember</option>
                <option value="Understand">Understand</option>
                <option value="Apply">Apply</option>
                <option value="Analyze">Analyze</option>
                <option value="Evaluate">Evaluate</option>
                <option value="Create">Create</option>
              </select>
            </div>
          </div>

          <div className="qem-form-group">
            <label>Đáp án</label>
            <div className="qem-options">
              {options.map((opt, idx) => (
                <div key={idx} className="qem-option-row">
                  <input 
                    type="radio" 
                    name="is_correct" 
                    checked={opt.is_correct} 
                    onChange={() => setCorrectOption(idx)}
                  />
                  <input 
                    type="text" 
                    value={opt.content} 
                    onChange={(e) => updateOptionContent(idx, e.target.value)}
                    className="qem-option-input"
                  />
                  <button className="qem-btn-icon" onClick={() => removeOption(idx)}><Trash size={18} /></button>
                </div>
              ))}
              <button className="qem-btn-add" onClick={addOption}><Plus size={16}/> Thêm đáp án</button>
            </div>
          </div>

          <div className="qem-form-group">
            <label>Giải thích</label>
            <textarea value={explanation} onChange={(e) => setExplanation(e.target.value)} rows={3} />
          </div>
        </div>
        <div className="qem-footer">
          <button className="qem-btn-cancel" onClick={onClose} disabled={loading}>Hủy</button>
          <button className="qem-btn-save" onClick={handleSave} disabled={loading}>Lưu thay đổi</button>
        </div>
      </div>
    </div>
  );
};
