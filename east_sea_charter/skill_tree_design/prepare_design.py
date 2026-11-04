import json,base64
from pathlib import Path
R=Path(__file__).resolve().parent
D=json.loads((R/'skills.json').read_text(encoding='utf8'))
V=Path(r'C:\Users\ADMIN\.codex\visualizations\2026\11\02\01a19c9d-9880-7ae2-8e9c-08d274cea911\skill-tree-review.html')
html=V.read_text(encoding='utf8')
html=html.replace('__SKILL_DATA__',json.dumps(D,ensure_ascii=False,separators=(',',':')))
for placeholder,file in [('__H_ATLAS__','heinrich-icons-H01-H24-preview.jpg'),('__S_ATLAS__','sariwa-icons-S01-S24-preview.jpg')]:
    html=html.replace(placeholder,'data:image/jpeg;base64,'+base64.b64encode((R/file).read_bytes()).decode())
assert '__SKILL_DATA__' not in html and '__H_ATLAS__' not in html and '__S_ATLAS__' not in html
assert '\\"' not in html and len(html.encode('utf8'))<1_000_000
V.write_text(html,encoding='utf8')
lines=['# Hiến Chương Đông Hải — Cây kỹ năng Heinrich & Sariwa',
       '', '**Bản thiết kế v1 · 48 node / biểu tượng · chưa đưa vào game.**', '',
       'Nguồn tham chiếu: `F:/Downloads/Hiến Chương Đông Hải – Mô tả Model LL & LH.md`. Những chi tiết trong tài liệu được dùng làm chất liệu thiết kế. Các hiệu ứng, tên phép, cấp mở và số liệu dưới đây là đề xuất mới, không phải nội dung đã có trong tài liệu hoặc đã hoạt động trong game.', '',
       '## 1. Trục thiết kế', '',
       '- Heinrich: bức tường thép ở tuyến trước, cầm kiếm và khiên; chỉ huy đoàn quân viễn chinh và học cách cai trị vùng đất mới.',
       '- Sariwa: con người, học giả kiêm tư tế Khuresh; pháp sư tầm xa gây sát thương lớn. Kiếm phục vụ tự vệ và thoát thân.',
       '- Cặp đôi: bùa Naga và lông vũ xanh được chuyển thành các node cá nhân; Hai Bờ, Một Lời Thề thưởng cho việc cùng quân đội.',
       '- Giữ sắc xanh lam–đồng của Heinrich và xanh ngọc–chàm của Sariwa. Icon Naga thể hiện tín ngưỡng/phép, không thể hiện Sariwa biến thành người rắn.',
       '- Không thêm unit lính mới. Skill quân đội chỉ tăng hiệu quả các nhóm quân có sẵn.', '',
       '## 2. Quy ước đọc cây', '',
       '“Cấp” là cấp nhân vật tối thiểu để mua bậc đầu. Mỗi bậc tốn 1 điểm; bậc sau yêu cầu bậc trước và ít nhất một cấp nhân vật tiếp theo. Tổng điểm nhánh chỉ tính điểm thật đã chi trong các node được ghi, không tính node có sẵn. “HOẶC” cho phép đi một trong hai đường; “VÀ” phải thỏa cả hai.', '',
       'Giả định để kiểm tra thiết kế: nhận 49 điểm từ cấp 2 đến 50. Heinrich có 54 điểm mua được; Sariwa có 52. Do đó cần chọn trọng tâm thay vì lấy trọn mọi thứ. Ngân sách này là giả định thiết kế, chưa phải xác nhận thiết lập trong mod.', '',
       'Sariwa bắt đầu với Nọc Ngọc bậc 1 và thuộc tính Âm Vang Ngọc Xà. Bậc 2 của mỗi phép mở bản cường hóa; nguy cơ phản phép cơ bản đề xuất 35%, rồi mới trừ các kỹ năng giảm rủi ro. Giá trị kháng dùng %, nguy cơ phản phép và bổ sung quân ghi theo điểm phần trăm.', '',
       'Các số trong dãy như 3/6/9 là tổng thưởng ở bậc 1/2/3, không cộng cả ba con số với nhau. Số liệu là điểm khởi đầu để cân bằng sau; chưa chốt sát thương tuyệt đối cho từng phép.', '',
       'Bất tử/khả năng quay lại sau khi bị thương được coi là thuộc tính nhân vật Legendary trong đề xuất này, không thêm một node tiêu điểm riêng. Không có nâng cấp thú cưỡi cho Sariwa trong bản đầu.', '']
for key in ['heinrich','sariwa']:
    hero=D[key];skills=hero['skills']
    total=sum(s['ranks']-s.get('free',0) for s in skills)
    assert len(skills)==24 and len(set(s['id'] for s in skills))==24
    assert total==(54 if key=='heinrich' else 52),(key,total)
    lines += ['## '+('3. ' if key=='heinrich' else '4. ')+hero['name'],'',hero['role']+'. '+hero['budget'],'']
    icon='heinrich-icons-H01-H24.png' if key=='heinrich' else 'sariwa-icons-S01-S24.png'
    lines += ['![Bảng phác thảo icon '+hero['name']+']('+str(R/icon).replace('\\','/')+')','']
    for branch in dict.fromkeys(s['branch'] for s in skills):
        lines += ['### '+branch,'','| Icon | Tên kỹ năng | Cấp · bậc | Điều kiện | Hiệu ứng dự kiến |','|---|---|---|---|---|']
        for s in [s for s in skills if s['branch']==branch]:
            rank='có sẵn' if s['ranks']==0 else str(s['ranks'])+' bậc'
            if s.get('free'):rank+='; bậc 1 miễn phí'
            lines.append('| '+s['id']+' | **'+s['name']+'** — '+s['type']+' | '+str(s['level'])+' · '+rank+' | '+s['prereq']+' | '+s['effect']+' |')
        lines += ['']
    prefix='H' if key=='heinrich' else 'S'
    lines += ['### Sơ đồ nhánh đặc hữu','','```mermaid','flowchart LR',f'  {prefix}17["{prefix}17 · '+skills[16]['name']+'"]',f'  {prefix}18["{prefix}18 · '+skills[17]['name']+'"]',f'  {prefix}19["{prefix}19 · '+skills[18]['name']+'"]',f'  {prefix}20["{prefix}20 · '+skills[19]['name']+'"]',f'  {prefix}21["{prefix}21 · '+skills[20]['name']+'"]',f'  {prefix}22["{prefix}22 · '+skills[21]['name']+'"]',f'  {prefix}17 --> {prefix}18',f'  {prefix}17 --> {prefix}19',f'  {prefix}19 --> {prefix}20',f'  {prefix}18 -->|Bậc 2| {prefix}21']
    if key=='heinrich':lines += ['  H18 -->|Bậc 2, đường chỉ huy| H22','  H20 -->|Hoặc đường lời thề| H22']
    else:lines += ['  S06["S06 · Ngũ Xà Phán Quyết"] -->|Đồng thời mở phép| S21','  S21 -->|Đường học thuật| S22','  S20 -->|Hoặc đường lời thề| S22']
    lines += ['```','']
lines += [
    '## 5. Kỹ năng chủ động và phối hợp', '',
    '**Heinrich:** Đứng Sau Ta bảo vệ đồng minh đang bị đánh; Giữ Vững Đầu Cầu củng cố tuyến bộ binh. Hai kỹ năng không cộng dồn phần tăng phòng thủ: lấy mức cao hơn. Tránh tạo một vùng bất tử chỉ nhờ bấm cả hai cùng lúc.', '',
    '**Sariwa:** Trói Bằng Rễ để làm chậm mục tiêu; Lột Vảy Cổ làm mềm giáp; sau đó chọn Nọc Ngọc cho mục tiêu đơn, Lưỡi Xà cho hàng quân, Mưa Vảy Ngọc cho cụm thiết giáp hoặc Ngũ Xà Phán Quyết cho vùng giao chiến quyết định. Các phép gây sát thương vùng đều phải báo trước và có rủi ro đánh trúng đồng minh.', '',
    '**Tình huống phối hợp:** Heinrich chặn đội hình địch, Sariwa giảm tốc và giảm giáp. Heinrich giữ sát mép vùng phép, Sariwa đánh vào phần sau đội hình. Khi đối phương áp sát Sariwa, dùng Phản Kiếm Ngọc Quang rút về phía Heinrich rồi dùng Đứng Sau Ta để che đường lui.', '',
    '**Hai Bờ, Một Lời Thề:** H20 chỉ tăng chỉ số của Heinrich; S20 chỉ tăng chỉ số của Sariwa. Mỗi người tự học node của mình; chỉ cần người kia có mặt trong cùng quân đội. Không cần cả hai cùng học và không tạo vòng lặp nhân thưởng. Trận có quân tiếp viện từ hai army riêng không thỏa điều kiện “cùng quân đội” trong bản đầu.', '',
    '## 6. Hai ngả chính trị chưa khóa', '',
    'Tài liệu gọi Phó Vương/Người của Khuresh và cán cân Hiến Chương–Thỏa Ước là ý tưởng tạm. Vì vậy H18 Ấn Tín Phó Vương và H19–H20 đều có thể học trong thiết kế này. Việc chọn model concept 3 trước đó là quyết định hình ảnh, không tự trở thành lựa chọn chính trị hay khóa quan hệ với Sariwa.', '',
    'Nếu sau này chốt cơ chế chính trị, tách phần thưởng chọn phe sang dilemma/đặc tính riêng. Không dùng một skill tiêu điểm để vô tình khóa vĩnh viễn một nhánh tình cảm. Giữ tên và icon hiện tại nếu có thể, rồi chỉ sửa điều kiện khi đã chốt cơ chế.', '',
    '## 7. Giới hạn cân bằng dự kiến', '',
    '- Heinrich có sát thương vừa đủ để giữ vai trò melee expert, nhưng đầu tư chống chịu phải cho hiệu quả rõ hơn so với nhồi sát thương. Phòng thủ tốt không đồng nghĩa miễn nhiễm bị bao vây hay bị bắn xuyên giáp.',
    '- Chống xung phong của H21 chỉ có thêm khi đi bộ, đứng yên và hướng đúng phía. Lên Griffon là lựa chọn cơ động, không giữ nguyên toàn bộ lợi thế giữ tuyến của bản đi bộ.',
    '- Sariwa không nhận giáp nặng, hồi máu lớn, bất tử giữa trận hoặc nhánh đấu tay đôi. S23–S24 chỉ mua thời gian rút lui.',
    '- Đề xuất trần cường độ phép của Sariwa ở 150% mức cơ bản; các nguồn giảm giá phép không đưa chi phí xuống dưới 2 năng lượng. Không thêm cơ chế hồi vô hạn để xóa điểm yếu cần nguồn phép.',
    '- Các thưởng chiến dịch của hai nhân vật có thể cộng với nhau theo giới hạn chung sẽ chốt sau. Mỗi nhân vật chỉ tồn tại một bản Legendary, không nhân bản để cộng nghiên cứu/ngoại giao nhiều lần.',
    '- Griffon là node dự phòng; nếu bản đầu chưa có mount và animation phù hợp, giữ nó trong tài liệu thay vì làm nút không hoạt động trong game.', '',
    '## 8. Chỉ dẫn icon', '',
    'Hai bảng icon là phác thảo mỹ thuật được tạo bằng imagegen, mỗi bảng 6 cột × 4 hàng; đọc từ trái sang phải, từ trên xuống dưới. H01–H24/S01–S24 khớp chính xác bảng kỹ năng. Bảng không phải atlas texture sẵn sàng nhập game: khi sản xuất cần tách từng icon, thống nhất kích thước và giản bớt chi tiết để đọc rõ ở 64 px.', '',
    'Heinrich dùng thép, nền xanh lam và đồng; điểm ngọc tập trung ở H19–H20/H22. Sariwa dùng xanh ngọc, chàm và đồng; lông vũ xanh ở S19–S20. Skill bị động dùng bố cục tĩnh, skill chủ động dùng động tác che chắn/va chạm, phép sát thương có hướng chuyển động rõ. Các bậc của cùng skill dùng chung một icon; số bậc do giao diện biểu thị.', '',
    '| Mã | Motif icon |','|---|---|']
for key in ['heinrich','sariwa']:
    for s in D[key]['skills']:lines.append('| '+s['id']+' | '+s['icon']+' |')
lines += ['', '## 9. Phạm vi bàn giao', '', 'Bản mô tả cây kỹ năng, hai bảng icon và bản xem tương tác để duyệt tên/nhánh. Chỉ ghi vào thư mục thiết kế và thư mục xem của chat. Không tạo hoặc sửa pack, database, script game, launcher hay file save trong yêu cầu này.', '']
(R/'Heinrich-Sariwa-Skill-Tree-v1.md').write_text('\n'.join(lines),encoding='utf8')
print('DESIGN_READY',total,'Sariwa points;',len(html.encode('utf8')),'bytes inline; 48 nodes')
