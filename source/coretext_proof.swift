import Foundation
import CoreText
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

let base = URL(fileURLWithPath: CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "outputs/Cairn-1.0", isDirectory: true)
let width = 1500, height = 1510
let colorSpace = CGColorSpaceCreateDeviceRGB()
let ctx = CGContext(data: nil, width: width, height: height, bitsPerComponent: 8, bytesPerRow: width * 4, space: colorSpace, bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
ctx.setFillColor(CGColor(red: 1, green: 0.988, blue: 0.96, alpha: 1)); ctx.fill(CGRect(x: 0, y: 0, width: width, height: height))
ctx.setShouldAntialias(true)
let ink = CGColor(red: 0.14, green: 0.19, blue: 0.20, alpha: 1)
func draw(_ text: String, _ font: CTFont, _ x: CGFloat, _ y: CGFloat) {
    let attributes: [NSAttributedString.Key: Any] = [NSAttributedString.Key(kCTFontAttributeName as String): font, NSAttributedString.Key(kCTForegroundColorAttributeName as String): ink]
    let line = CTLineCreateWithAttributedString(NSAttributedString(string: text, attributes: attributes))
    ctx.textPosition = CGPoint(x: x, y: CGFloat(height) - y)
    CTLineDraw(line, ctx)
}
let labelFont=CTFontCreateWithName("Menlo" as CFString,18,nil)
draw("CAIRN / NATIVE macOS CORE TEXT / NO INSTALLATION",labelFont,35,42)
var result: [[String:Any]]=[]
for (index, style) in ["Regular","Italic","Bold","BoldItalic"].enumerated() {
    let url = base.appendingPathComponent("desktop/Cairn-\(style).ttf")
    guard let provider = CGDataProvider(url: url as CFURL), let cgfont = CGFont(provider) else { fatalError("Could not decode \(style)") }
    let font=CTFontCreateWithGraphicsFont(cgfont,18,nil,nil)
    let family=CTFontCopyFamilyName(font) as String
    let name=CTFontCopyPostScriptName(font) as String
    precondition(family=="Cairn" && name=="Cairn-\(style)")
    let traits=CTFontGetSymbolicTraits(font)
    precondition(traits.contains(.traitBold)==style.contains("Bold"))
    precondition(traits.contains(.traitItalic)==style.contains("Italic"))
    let top=100+CGFloat(index)*345
    draw(style,labelFont,35,top)
    draw("The broken crown beneath the mountain.",CTFontCreateCopyWithAttributes(font,36,nil,nil),35,top+60)
    for (j,size) in [12.0,14.0,16.0,18.0,20.0].enumerated() {
        let y=top+105+CGFloat(j)*36
        draw("\(Int(size)) px",CTFontCreateCopyWithAttributes(labelFont,12,nil,nil),35,y)
        draw("The quiet keeper reads the names. minimum rn m Il1 O0 aeog ij ft.",CTFontCreateCopyWithAttributes(font,size,nil,nil),105,y)
    }
    draw("“Names”—and words… ‘rain’ © ¥ § ¦ ¤ «stone» @ [01:11]",CTFontCreateCopyWithAttributes(font,22,nil,nil),35,top+308)
    result.append(["style":style,"family":family,"postscript_name":name,"native_decode":"passed","native_style_traits":"passed","glyphs":CTFontGetGlyphCount(font)])
}
let image=ctx.makeImage()!
let output=base.appendingPathComponent("proofs/macos-coretext.png")
let dest=CGImageDestinationCreateWithURL(output as CFURL,UTType.png.identifier as CFString,1,nil)!
CGImageDestinationAddImage(dest,image,nil);precondition(CGImageDestinationFinalize(dest))
let data=try JSONSerialization.data(withJSONObject:result,options:[.prettyPrinted,.sortedKeys])
try data.write(to:base.appendingPathComponent("macos-validation.json"))
print(String(data:data,encoding:.utf8)!)
