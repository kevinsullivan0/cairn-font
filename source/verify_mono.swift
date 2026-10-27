import Foundation
import CoreText
let names=CTFontManagerCopyAvailablePostScriptNames() as! [String]
var report:[[String:Any]]=[]
for style in ["Regular","Italic","Bold","BoldItalic"] {
 let name="CairnMono-"+style
 let font=CTFontCreateWithName(name as CFString,18,nil)
 guard names.contains(name), CTFontCopyPostScriptName(font) as String == name else {fatalError("Font unavailable: \(name)")}
 let traits=CTFontGetSymbolicTraits(font)
 guard traits.contains(.traitMonoSpace) else {fatalError("Mono trait missing")}
 let text="AV != fn(x) -> 0;"
 let string=NSAttributedString(string:text,attributes:[NSAttributedString.Key(kCTFontAttributeName as String):font])
 let line=CTLineCreateWithAttributedString(string)
 let width=CTLineGetTypographicBounds(line,nil,nil,nil)
 guard abs(width-Double(text.count)*13.5)<0.001 else {fatalError("Shaped advance mismatch: \(width)")}
 report.append(["name":name,"registered":true,"monospace_trait":true,"shaped_advance":width,"expected_advance":Double(text.count)*13.5])
 print("Verified native monospace: \(name)")
}
let data=try JSONSerialization.data(withJSONObject:report,options:[.prettyPrinted,.sortedKeys])
try data.write(to:URL(fileURLWithPath:CommandLine.arguments[1]))
