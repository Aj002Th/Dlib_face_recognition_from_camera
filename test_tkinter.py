class Biggest:
    def __init__(self, data) -> None:
        self.data = Data(data)
        self.operate = Operate(self.data)
    
    def run(self):
        self.operate.addData()
        print(f'self.data: {self.data.data}')
        print(f'self.operate.data: {self.operate.data.data}')
        

class Operate:
    def __init__(self, data) -> None:
        self.data = data
    
    def addData(self):
        self.data.data += 1

class Data:
    def __init__(self, data) -> None:
        self.data = data

def main():
    data = 1
    biggest = Biggest(data)
    biggest.run()

if __name__ == "__main__":
    main()
    