from cyberbrain import trace
@trace
def sum():
    a = input("Enter number one: ")
    b = input("Enter number two: ")
    return a + b
if __name__ == "__main__":
    print(sum())

number = raw_input("Tell me a number: ")
number = float(number)
if number % 2 == 0:
    print ("number is even.")
elif number % 2 == 1:
    print (number,"number is odd")
else:
    print (number, "is very strange")