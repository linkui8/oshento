from config import products, min, max, bpmj


class Man():
    def __init__(self, weight, val_of_product, type):
        self.weight = weight
        self.bpm = 90
        self.is_death = False
        self.val_of_product = val_of_product
        self.type = type

    def val_of_toxic(self):
        self.val_of_toxicc = (float(self.val_of_product) / 1000) * products[self.type]
        return self.val_of_toxicc
    
    def val_of_blood(self):
        self.blood = self.weight * 0.15
        return self.blood
    
    def death(self):
        a = float(self.val_of_toxic())
        b = int(self.val_of_blood())
        self.plot = a / b
        if self.plot < min:
            self.itog = "Всё в порядке"
        elif self.plot > min and self.plot < ((min + max) / 2):
            self.itog = "Кислоты мало, но могут появиться проблемы"
        elif self.plot > ((min + max) / 2) and self.plot < max:
            self.itog = "Кислоты достаточно для серьёзных проблем"
        else:
            self.itog = "Организм не выдержал, смерть"
        return f"{self.itog}, количество синильной кислоты в крови - {round(self.plot, 2)}мг/л \
                \n Время, за которое токсин прошёл из ротовой полости в желудок - {bpmj[1][1]}c(скорость - {bpmj[1][2]}, расстояние - {bpmj[1][0]})\
                \n Время, за которое токсин прошёл из желудка в печень - {bpmj[2][1]}c(скорость - {bpmj[1][2]}, расстояние - {bpmj[1][0]})\
                \n Время, за которое токсин прошёл из печени в сердце -{bpmj[3][1]}c(скорость - {bpmj[1][2]}, расстояние - {bpmj[1][0]}) \
                \n Общее время, за которое токсин дошёл до сердца - {bpmj[1][1] + bpmj[2][1] + bpmj[3][1]}"
    


print(Man(50, 5, "apple").death())



#time to heart
#death-not death  !!!!!!!!!!!!
#model