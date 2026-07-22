import sys
import os

# Add the backend directory to sys.path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.course import Course
from app.core.security import get_password_hash

def seed_db():
    db = SessionLocal()
    try:
        print("Bắt đầu khởi tạo dữ liệu mẫu (Seeding)...")

        # 1. Tạo tài khoản Admin
        admin_email = "admin@gmail.com"
        admin_user = db.query(User).filter(User.email == admin_email).first()
        if not admin_user:
            admin_user = User(
                email=admin_email,
                hashed_password=get_password_hash("admin123"),
                full_name="Quản trị viên",
                role="admin",
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print(f"✅ Đã tạo tài khoản Admin: {admin_email} | Pass: admin123")
        else:
            print(f"🔹 Tài khoản Admin {admin_email} đã tồn tại.")

        # 2. Tạo tài khoản Lecturer
        lecturer_email = "gv1@gmail.com"
        lecturer_user = db.query(User).filter(User.email == lecturer_email).first()
        if not lecturer_user:
            lecturer_user = User(
                email=lecturer_email,
                hashed_password=get_password_hash("gv123"),
                full_name="Giảng viên Trần Văn A",
                role="lecturer",
                is_active=True
            )
            db.add(lecturer_user)
            db.commit()
            db.refresh(lecturer_user)
            print(f"✅ Đã tạo tài khoản Giảng viên: {lecturer_email} | Pass: gv123")
        else:
            print(f"🔹 Tài khoản Giảng viên {lecturer_email} đã tồn tại.")

        # 3. Tạo Khóa học mẫu
        course_code = "CS101"
        course = db.query(Course).filter(Course.code == course_code).first()
        if not course:
            course = Course(
                code=course_code,
                title="Nhập môn Khoa học Máy tính",
                description="Khóa học cơ bản về lập trình và khoa học máy tính dành cho người mới bắt đầu.",
                is_deleted=False,
                created_by=admin_user.id
            )
            db.add(course)
            db.commit()
            db.refresh(course)
            print(f"✅ Đã tạo Khóa học mẫu: {course_code} - {course.title}")
        else:
            print(f"🔹 Khóa học {course_code} đã tồn tại.")

        print("Hoàn tất Seeding!")

    except Exception as e:
        print(f"❌ Lỗi khi seed dữ liệu: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
