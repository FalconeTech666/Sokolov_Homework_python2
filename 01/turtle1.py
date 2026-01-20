import turtle


# создание и настройка экрана
screen = turtle.Screen()
screen.setup(600, 600)

# создание и настройка черепахи
t = turtle.Turtle('turtle')
t.speed(0)
t.color('blue')


def move_up():
    t.setheading(90) # установка направления в градусах
    t.forward(10) # вперед на 10 пикселей

def move_down():
    t.setheading(270)
    t.forward(10)

def move_left():
    t.setheading(180)
    t.forward(10)

def move_right():
    t.setheading(0)
    t.forward(10)


# управление курсорными стрелками
screen.onkey(move_up, 'Up')
screen.onkey(move_down, 'Down')
screen.onkey(move_left, 'Left')
screen.onkey(move_right, 'Right')
screen.listen() # слушать нажатые клавиши


screen.mainloop()  # отрисовка окна пока не закроют крестиком
