-- Tautan ke file lokal (mis. ../backend/app/rules.py) tidak bisa dibuka dari PDF, jadi diubah menjadi teks biasa.
function Link(el)
  local t = el.target
  if t:match("^https?://") or t:match("^#") then return el end
  return el.content
end

-- Gambar yang berdiri sendiri dalam satu paragraf dijadikan figure dengan keterangan (alt text).
function Para(el)
  if #el.content == 1 and el.content[1].t == "Image" then
    local img = el.content[1]
    return pandoc.Figure(pandoc.Plain{img}, {pandoc.Plain(img.caption)})
  end
end
