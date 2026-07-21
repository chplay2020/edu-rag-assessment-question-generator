#!/bin/bash
echo "Đang khởi tạo dữ liệu mẫu (Seed Data)..."
docker compose exec backend python seed_data.py
echo "Hoàn tất!"
