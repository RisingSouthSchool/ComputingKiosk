init = function()
item_x = random.nextInt(160) - 80
item_y = 100
item_speed = 2
player_x = 0
player_y = -75
score = 0 
lives = 3
alive = true 
haz_x = random.nextInt(160) - 80
haz_y = 70
haz_speed = 4

end

update = function() 
  if keyboard.RIGHT then x = x+4 
    end
  if keyboard.LEFT then x = x-5 
  end
  if alive == false then
    return 
  end
item_y -= item_speed
if item_y < -110 then
  item_y = 100
  item_x = random.nextInt(160) - 80
end

dx = player_x - item_x 
dy = player_y - item_y
if dx*dx + dy*dy < 250 then
  score += 1 
  item_x = random.nextInt(160) - 80
  item_y = 100
end


end

  dx = player_x - item2_x
  dy = player_y - item2_y
  if dx*dx + dy*dy <250 then 
    score += 1
    item2_x = random.nextInt(160) - 80
    item2_y = 100
end
haz_y -= haz_speed
if haz_y < -110 then
  haz_y = 100
  haz_ = random.nextInt(160) - 80
end
dx = player_x - haz_x
dy = player_y - haz_y
if dx*dx + dy*dy < 250 then 
  lives -= 1
  haz_x = random.nextInt(160) - 80
  haz_y = 100
  end
if lives <= 0 then
  alive = false
  
end
  
draw = function()
  screen.drawSprite("background", 0,0, screen.width)
  screen.drawSprite("player", x, y -75, 20)
  screen.drawSprite("item", item_x, item_y, 17, 17)
  screen.drawSprite("hazard", haz_x, haz_y, 17,17)
  screen.drawSprite("item", item2_x, item2_y, 10, 10) 
  screen.drawText("Score: " + score, 0, 90, 12,"rgb(255,255,255)")
  screen.drawText("Lives: " + lives, -70, 90, 12,"rgb(255,100,100)")
 screen.drawSprite("item", item2_x, item2_y, 10,10)
  if alive == false then
  screen.drawText("GAME OVER", 0, 10, 15, "rgb(230,60,80)")
  end 

end















