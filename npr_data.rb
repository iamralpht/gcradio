
require 'net/http'
require 'date'
require 'rubygems'
require 'json'
require 'sanitize'

date_string = ARGV.first

host="api.npr.org"
data=[]
base_search_url = "/query?fields=title,audio,textWithHtml&requiredAssets=audio&dateType=story&output=JSON&numResults=20&apiKey=MDExOTExMzk1MDEzNzU3MjcwMDUyNDEyMA001"
programs={"All Songs Considered"=>37,
  "All Things Considered"=>2,
  "Ask Me Another"=>58, 
  "Fresh Air from WHYY"=>13,
  "Here & Now"=>60,
  "Morning Edition"=>3,
  "Science Friday"=>61,
  "TED Radio Hour"=>57,
  "Tell Me More"=>46,
  "Wait Wait...Don't Tell Me!"=>35,
  "Weekend Edition Saturday"=>7,
  "Weekend Edition Sunday"=>10,
  "World Cafe"=>39,
  "World of Opera"=>36
  }
programs.each do |k,v|
  program_url = base_search_url+"&id=#{v}"
  search_url = program_url+"&date="+date_string
  response = Net::HTTP.get_response(host,search_url)
  response_hash=JSON.parse(response.body)
  if not response_hash.keys.include? "message"
    stories = response_hash["list"]["story"]
    stories.each do |s|
      if s["textWithHtml"]
        
        
        full_text=s["textWithHtml"]["paragraph"].collect{|par| par["$text"]}.join(" ")
        clean_text=Sanitize.clean(full_text)
        puts full_text.size.to_s+" "+clean_text.size.to_s
        
        data<<{"program_id"=>v,
          "program_name"=>k,
          "story_id"=>s["id"],
          "story_title"=>s["title"],
          "image_url"=>s["image"].first["src"],
          "audio_url"=>s["audio"].first["format"]["mp4"]["$text"],
          "text"=>s["textWithHtml"]["paragraph"].collect{|par| par["$text"]}.join(" ")
        }
      end
    end
  end
end

File.open("public/stories_full_text.json","w") do |f|
  f.write(data.to_json)
end


