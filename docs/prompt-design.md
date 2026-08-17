# Prompt Design

Prompt nằm ở `backend/app/ai/prompts/*.txt`, được nạp qua registry
`app/ai/prompts/__init__.py` (`load_prompt`, `render_prompt`, `prompt_version`).

## 1. Quy ước

- Placeholder viết dạng `{ten_bien}` và được thay bằng `str.replace`. Cố ý
  không dùng `str.format` vì thân prompt chứa rất nhiều dấu ngoặc nhọn của JSON.
- Mỗi prompt có version trong `PROMPT_VERSIONS`. Tăng version mỗi khi sửa nội
  dung; version được ghi vào log mỗi lần sinh câu hỏi để so sánh chất lượng
  giữa các phiên bản (T049).
- Prompt được cache sau lần đọc đầu tiên.

## 2. Danh sách prompt

| File                      | Version | Dùng ở đâu                            |
| ------------------------- | ------- | ------------------------------------- |
| `generate_mcq.txt`        | v2      | `generation/question_generator.py`    |
| `repair_questions.txt`    | v1      | dành cho vòng sửa câu hỏi hỏng        |
| `validate_question.txt`   | v2      | `validation/llm_judge.py`             |
| `classify_bloom.txt`      | v1      | tham chiếu cho classifier bằng luật   |
| `classify_difficulty.txt` | v1      | tham chiếu cho classifier bằng luật   |

## 3. `generate_mcq.txt`

Biến: `{context}`, `{number_of_questions}`, `{difficulty}`, `{bloom_level}`,
`{language}`, `{chunk_ids}`, `{avoid_questions}`.

Prompt chia làm hai nhóm luật:

**Hard rules** - vi phạm là bị loại ở tầng validate: đúng 4 phương án, đúng 1
phương án đúng, `correct_answer` khớp từng ký tự với phương án đúng,
`source_chunk_ids` chỉ chứa ID có trong `{chunk_ids}`.

**Quality rules** - những lỗi mà LLM hay mắc khi sinh MCQ và làm câu hỏi mất
giá trị đánh giá:

- Câu hỏi phải đứng độc lập, không viết "theo đoạn văn trên".
- Phương án nhiễu phải hợp lý với người chưa học, sai rõ với người đã học.
- Bốn phương án dài xấp xỉ nhau; đáp án đúng không được dài nhất (đây là dấu
  hiệu lộ đáp án phổ biến nhất, và cũng được kiểm lại bằng luật ở
  `question_validator`).
- Cấm "tất cả các đáp án trên" / "không đáp án nào".
- Tránh câu phủ định ("phương án nào KHÔNG...").
- Trải câu hỏi qua nhiều chunk và nhiều ý khác nhau.

`{avoid_questions}` chứa các câu đã sinh ở lượt trước, dùng cho vòng sinh bù để
model không hỏi lại cùng một ý.

Model được gọi ở JSON mode với `MCQ_RESPONSE_SCHEMA`, nên phần mô tả schema
trong prompt chủ yếu đóng vai trò nhắc lại ngữ nghĩa từng trường.

## 4. `validate_question.txt`

Biến: `{context}`, `{questions}`.

Chấm cả lô trong một lần gọi, trả về mảng `verdicts` kèm `index` để ghép lại
đúng câu. Phân biệt rõ:

- `errors` (đặt `is_valid=false`): câu hỏi không trả lời được từ context, đáp
  án đúng thật ra sai, nhiều phương án cùng đúng, giải thích mâu thuẫn context.
- `warnings`: câu hỏi dùng được nhưng mơ hồ, phương án nhiễu kém, đáp án đúng
  dài bất thường, nhãn độ khó/Bloom không khớp mức tư duy thực tế.

Điểm số gồm `grounding`, `clarity`, `distractor_quality`, `assessment_quality`
trong khoảng 0.0-1.0. Trung bình dưới `LLM_JUDGE_MIN_SCORE` thì câu hỏi bị đẩy
sang `review_required`.

## 5. `repair_questions.txt`

Biến: `{context}`, `{chunk_ids}`, `{language}`, `{invalid_questions}`.

Nhận các câu đã fail validate kèm đúng thông báo lỗi, yêu cầu model viết lại
cho hợp lệ và cho phép bỏ hẳn câu nào context không đỡ nổi. Hiện pipeline chọn
cách sinh bù câu mới (rẻ và ổn định hơn); prompt này để dành cho trường hợp cần
giữ nguyên ý của câu hỏi gốc.

## 6. Khi sửa prompt

1. Sửa file `.txt`.
2. Tăng version tương ứng trong `PROMPT_VERSIONS`.
3. Chạy lại `backend/tests/test_ai_question_generator.py` - test này kiểm tra
   prompt có chứa đủ phần yêu cầu (`number_of_questions`, `difficulty`,
   `bloom_level`, `language`) và nội dung context.
