#Requires AutoHotkey v2.0
#SingleInstance Force
; ===================================================================
;  ColorPicker.ahk  —  取色器（给色弱用户的「用数字代替眼睛」工具）
;
;  用法：按 Ctrl + Alt + C 开始取色
;        移动鼠标 → 提示框实时显示光标下像素的 HEX / RGB / HSV
;        左键单击 → 把 HEX 复制到剪贴板并结束
;        右键 / Esc → 取消
;
;  说明：HEX 直接就是网页下拉框里那种写法（#800000），
;        把它和选项里的字符串逐字对比即可，不需要辨认颜色。
; ===================================================================

PICK_KEY := "^!c"          ; ← 想换热键改这里（^=Ctrl ! =Alt +=Shift # =Win）

; 让脚本按「物理像素」取坐标，避免高分屏缩放导致取到隔壁像素
try DllCall("SetProcessDpiAwarenessContext", "ptr", -4, "int")

hdc := DllCall("GetDC", "ptr", 0, "ptr")

Hotkey PICK_KEY, StartPick

StartPick(*) {
    global hdc
    Hotkey PICK_KEY, "Off"
    Hotkey "LButton", CopyColor, "On"
    Hotkey "RButton", CancelPick, "On"
    Hotkey "Esc", CancelPick, "On"
    SetTimer(ShowTip, 25)
    ShowTip()
}

ShowTip() {
    global hdc
    MouseGetPos &mx, &my
    c := DllCall("GetPixel", "ptr", hdc, "int", mx, "int", my, "uint")
    if (c = 0xFFFFFFFF)
        text := "此处无法取色"
    else
        text := HexOf(c) "`nRGB " RGBof(c) "`n" HSVof(c)
    ToolTip text, mx + 22, my + 22
}

CopyColor(*) {
    global hdc
    MouseGetPos &mx, &my
    c := DllCall("GetPixel", "ptr", hdc, "int", mx, "int", my, "uint")
    StopPick()
    if (c = 0xFFFFFFFF) {
        ToolTip "此处无法取色"
        SetTimer () => ToolTip(), -1500
        return
    }
    hex := HexOf(c)
    A_Clipboard := hex
    ToolTip "已复制  " hex
    SetTimer () => ToolTip(), -1500
}

CancelPick(*) {
    StopPick()
    ToolTip "已取消"
    SetTimer () => ToolTip(), -900
}

StopPick() {
    global hdc, PICK_KEY
    SetTimer ShowTip, 0
    Hotkey "LButton", "Off"
    Hotkey "RButton", "Off"
    Hotkey "Esc", "Off"
    Hotkey PICK_KEY, StartPick, "On"
    ToolTip
}

HexOf(c) {
    return Format("#{:02X}{:02X}{:02X}", c & 0xFF, (c >> 8) & 0xFF, (c >> 16) & 0xFF)
}

RGBof(c) {
    return Format("({}, {}, {})", c & 0xFF, (c >> 8) & 0xFF, (c >> 16) & 0xFF)
}

; 取到的像素值（BGR 打包）→ HSV
;   V = max/255        （最大通道，即这个颜色最亮那一档）
;   S = (max-min)/max  （离灰色有多远：S=0 就是灰）
;   H = 看哪条通道是 max，再在 60° 一格里线性插值
HSVof(c) {
    r := c & 0xFF, g := (c >> 8) & 0xFF, b := (c >> 16) & 0xFF
    mx := Max(r, g, b), mn := Min(r, g, b), d := mx - mn
    if (d = 0)
        h := 0                      ; 灰色没有色相
    else if (mx = r)
        h := 60 * Mod((g - b) / d, 6)
    else if (mx = g)
        h := 60 * ((b - r) / d + 2)
    else
        h := 60 * ((r - g) / d + 4)
    if (h < 0)
        h += 360
    s := (mx = 0) ? 0 : d / mx * 100
    v := mx / 255 * 100
    return Format("HSV  H {}°  S {}%  V {}%", Round(h), Round(s), Round(v))
}
