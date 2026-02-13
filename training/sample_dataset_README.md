## Dataset format (folder-based)

TH: วางรูปเป็นโฟลเดอร์ตามชื่อบุคคล  
EN: Put images in per-person folders.

Example:

```
dataset/
  Alice/
    001.jpg
    002.jpg
  Bob/
    001.jpg
  unknown/
    u001.jpg
```

Tips:
- ใช้รูปหลายมุม/หลายแสง (หลายวัน) จะทนกว่า
- ความคมชัดและหน้าตรงช่วยให้เทรนง่ายขึ้น
- “unknown/” เป็นทางเลือก: จะไม่ถูกเทรนเป็น class จริง แต่ใช้ทดสอบ threshold ได้

