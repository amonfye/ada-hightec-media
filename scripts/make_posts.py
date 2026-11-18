from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, random, sys, json

W, H = 1080, 1350
F = '/usr/share/fonts/opentype/inter/'
src = Image.open('assets/template_ref.png').convert('RGB')

# accent colour sampled from "en 2 minutes." line of the existing carousel
px = np.array(src.crop((60, 700, 1000, 780))).reshape(-1, 3)
blue = px[(px[:, 2] > 200) & (px[:, 0] < 120)]
ACC = tuple(int(v) for v in np.median(blue, 0)) if len(blue) else (56, 189, 248)
WHITE = (241, 245, 255)
MUTED = (178, 184, 212)
ICON = src.crop((68, 68, 158, 158))


def background(seed):
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    img = np.zeros((H, W, 3)) + np.array([13, 11, 34])
    def glow(cx, cy, r, col, k=1.0):
        d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
        a = np.clip(1 - d, 0, 1) ** 1.6 * k
        return a[..., None] * (np.array(col) - np.array([13, 11, 34]))
    img += glow(880, 60, 900, (58, 40, 132))
    img += glow(-60, 760, 700, (4, 92, 142), 0.95)
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im, 'RGBA')
    rnd = random.Random(seed)
    x = 40
    while x < W - 20:
        h = rnd.randint(60, 300)
        d.rectangle([x, H - h, x + 29, H], fill=(36, 28, 84, 210))
        x += 43
    return im


def font(name, size):
    return ImageFont.truetype(F + name, size)


def wrap(draw, text, fnt, maxw):
    words, lines, cur = text.split(' '), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if draw.textlength(t, font=fnt) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    return lines


def post(spec, out, seed):
    im = background(seed)
    d = ImageDraw.Draw(im, 'RGBA')
    # header
    im.paste(ICON, (68, 68))
    d.text((176, 113), 'ADA Hightec', font=font('Inter-Bold.otf', 36), fill=WHITE, anchor='lm')
    if spec.get('tag'):
        tf = font('Inter-Bold.otf', 22)
        tw = d.textlength(spec['tag'], font=tf)
        d.rounded_rectangle([1010 - tw - 36, 94, 1010, 134], 20, outline=(90, 80, 150), width=2)
        d.text((1010 - tw / 2 - 18, 114), spec['tag'], font=tf, fill=MUTED, anchor='mm')
    # title: list of (text, colour) lines-groups
    y = spec.get('y', 360)
    size = spec.get('size', 106)
    tf = font('InterDisplay-Bold.otf', size)
    for chunk, col in spec['title']:
        for line in wrap(d, chunk, tf, 940):
            d.text((70, y), line, font=tf, fill=ACC if col == 'a' else WHITE)
            y += int(size * 1.1)
    y += 30
    if spec.get('body'):
        bf = font('Inter-Regular.otf', 36)
        for para in spec['body'].split('\n'):
            for line in wrap(d, para, bf, 920):
                d.text((70, y), line, font=bf, fill=MUTED); y += 50
    if spec.get('list'):
        y += 10
        nf = font('Inter-Bold.otf', 30); lf = font('Inter-SemiBold.otf', 40); sf = font('Inter-Regular.otf', 28)
        for i, (a, b) in enumerate(spec['list'], 1):
            d.ellipse([70, y, 122, y + 52], fill=ACC)
            d.text((96, y + 26), str(i), font=nf, fill=(13, 11, 34), anchor='mm')
            d.text((146, y - 2), a, font=lf, fill=WHITE)
            if b:
                d.text((146, y + 46), b, font=sf, fill=MUTED)
            y += 112
    if spec.get('cta'):
        d.text((70, 1220), spec['cta'], font=font('Inter-SemiBold.otf', 34), fill=ACC)
    im.save(out, quality=92)


if __name__ == '__main__':
    specs = json.load(open(sys.argv[1]))
    for i, s in enumerate(specs):
        post(s, s['file'], seed=i * 11 + 3)
        print(s['file'])
