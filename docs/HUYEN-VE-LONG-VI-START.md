# Huyen Ve bắt đầu tại Long Vi — v25 r7

03/11/2026: người dùng yêu cầu chuyển vị trí khởi đầu của Huyen Ve về Long Vi.
R7 đã cài/bật; r6 tắt, giữ làm rollback. SHA256 pack:
`7688bf9369353f10f253d43c7c3f4ba7085a27db2dbddd8628812456b2704a66`.

Script `mc_huyen_ve_start_at_long_vi.lua` dùng native pre-first-tick callback,
kiểm tra `is_new_game`, tìm điểm đất hợp lệ cạnh Long Vi đang thuộc Agents of
the Moon và teleport chính commander Huyen Ve cùng quân đoàn hiện có. Không
tạo lại Lord/units hoặc đổi cấp, trang bị, tỉnh, thành, garrison. Áp dụng cho
campaign mới có tên script main_warhammer/cr_combi_expanded và region Long Vi,
cả player/AI. Nếu không có vị trí hợp lệ thì giữ nguyên, ghi log.

Không sửa ESF/startpos hoặc save trực tiếp. Save đang chơi không được dịch chuyển.
Để xem vị trí khởi đầu mới cần tạo campaign mới; frontend placeholder/map preview
không được sửa trong lần này. Các file cũ của r6 byte-identical, chỉ thêm một Lua.
Native API xác minh trong local lib_campaign_manager.lua: teleport_to và
add_pre_first_tick_callback là API cho việc bố trí nhân vật lúc tạo campaign.

10 trường hợp Lua giả lập đạt: new game, saved marker, tải save, sai campaign,
Long Vi không thuộc faction, thiếu đất, đã ở Long Vi, teleport thất bại,
campaign alias IEE và AI. Các hồi quy quest cũ vẫn đạt. Đây chưa phải xác nhận
trong game; cần kiểm tra campaign mới/camera/vị trí thực tế.

Báo cáo: build/huyen-ve-v25-quest-chain/long-vi-start-validation-r7.json,
lua-regression.json và deployment.json. Full builder giữ script trong các revision sau.
