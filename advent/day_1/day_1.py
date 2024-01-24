def find_calibration(input_text):
    calibration_nums = []
    for line in input_text:
        first_number = 0
        second_number = -1
        for c in line:
            if c.isdigit():
                if not first_number:
                    first_number = c
                else:
                    second_number = c
        if second_number == -1:
            second_number = first_number

        calibration_nums.append(f"{first_number}{second_number}")

    return calibration_nums

def find_calibrations_v2(input_text):
    calibration_nums = []
    for line in input_text:

        digits = {
        'zero': '0', 'one': '1', 'two': '2', 'three': '3', 
        'four': '4', 'five': '5', 'six': '6', 'seven': '7', 
        'eight': '8', 'nine': '9'
        }

        first_number_positions = [line.find(digit[key]) for keys in digits.keys() if line.find(digit[key]) != -1]
        first_number_positions = [line.find(key) for key in digits.keys() if line.find(key) != -1]
        first_number = line[min(first_number_positions, default=-1)]

        second_number_positions = [line.rfind(digit) for digit in digits]
        second_number = line[max(second_number_positions, default=-1)]

        calibration_nums.append(f"{first_number}{second_number}")

    return calibration_nums

if __name__ == "__main__":
    load = open("test_2.txt", "r")
    input_text = load.readlines()
    load.close()

    calibration = find_calibration(input_text)
    calibration_2 = find_calibrations_v2(input_text)
    
    sum_1 = 0
    for calibration_num in calibration:
        sum_1 += int(calibration_num)
        
    sum_2 = 0
    print(calibration_2)
    for calibration_num in calibration_2:
        sum_2 += int(calibration_num)
        
    print("\ncalibration is: ", sum_1)
    print("\ncalibration 2 is: ", sum_2)
    # print("\nvalues are:")
    # for i in calibration:
    #     print(i)

        
            

            


        