
MORTGAGE_LENGTHS = 30
APR = .03
APR_FACTOR = 1.93
monthly = 337.28
HOME_VALUE_TARGET = 100000
DOWN_PAYMENT_PERCENTAGE = .2
RI_YRLY_APPR = .04
ETF_YRLY_DRAW = .04
MONTHS_IN_YEAR = 12
MAX_HOUSES = 10
class House:

    def __init__(self, cost, down):
        self.initial_value = cost
        self.appr_value = cost
        self.equity = down
        self.p_owed = cost - down
        total_owed = self.p_owed + self.p_owed/APR_FACTOR
        self.i_owed = total_owed - self.p_owed
        self.MONTHLY = total_owed/MONTHS_IN_YEAR/MORTGAGE_LENGTHS
        
    #a monthly step
    def step(self):
        if self.equity < self.initial_value:
            interest = APR/MONTHS_IN_YEAR*self.p_owed
            principal = self.MONTHLY - interest
            self.p_owed -= principal
            self.equity += principal
            self.i_owed -= interest
        self.appr_value *= (1 + (RI_YRLY_APPR/MONTHS_IN_YEAR))#.04 is yrly RI ^
        
    def get_monthly_income(self):
        NOI = self.appr_value/15
        NOI *= .85 #CAPEX
        NOI *= 1/MONTHS_IN_YEAR
        if self.equity < self.initial_value:
            NOI -= self.MONTHLY
        return NOI
    
    def print_house(self):
        print("\n")
        print("RED: " + str(self.getRed()))
        print("GREEN: " + str(self.equity))
        print("VALUE: " + str(self.appr_value))
        print("BRINGIN IN MONTHLY: " + str(self.get_monthly_income()))
        print("\n")

    def refi(self):
        down = self.appr_value * DOWN_PAYMENT_PERCENTAGE
        cash_loan_out = self.appr_value - down
        net_cash_out = cash_loan_out + self.equity - down
        self.equity = down
        self.p_owed = cash_loan_out
        total_owed = self.p_owed + self.p_owed/APR_FACTOR
        self.i_owed = total_owed - self.p_owed
        self.MONTHLY = total_owed/MONTHS_IN_YEAR/MORTGAGE_LENGTHS
        return net_cash_out
        
    def payOff(self):
        owed = self.p_owed
        self.p_owed = 0
        self.equity = self.initial_value
        return owed
    
    def getGreen(self):
        return self.equity
    def getRed(self):
        if self.equity >= self.initial_value:
            return 0
        else:
            return self.p_owed
            
            
cash = 25000
monthly_income = 0
houses = []

months = 0
while monthly_income < 10000 or months < 360:
    months += 1
    if months%MONTHS_IN_YEAR == 0:
        print("----------------------------------------------------------------------VVV-YEAR"+str(months//MONTHS_IN_YEAR)+"-VVV--------------------------------------------------------------")
        for i in range(len(houses)):
            print("\n")
            print("HOUSE " + str(i) + ":")
            houses[i].print_house()
        print("----------------------------------------------------------------------^^^-YEAR"+str(months//MONTHS_IN_YEAR)+"-^^^------------------------------------------------------------")

    down = HOME_VALUE_TARGET * DOWN_PAYMENT_PERCENTAGE
    while cash > down and len(houses) < MAX_HOUSES:
        houses.append(House(HOME_VALUE_TARGET,down))
        cash -= down
    for h in houses:
        h.step()
        if h.getGreen() + h.appr_value - h.initial_value > 2 * down and len(houses) < MAX_HOUSES:
            print("\n\n\nREFIIIIIII\n\n")
            cash += h.refi()
    
    if len(houses) == MAX_HOUSES:
        for h in houses:
        
            if h.getRed() != 0 and h.getRed() < cash:
                print("paYOFF")
                cash -= h.payOff()

    cash += monthly_income
    new_monthly_income = 0
    for h in houses:
        
        new_monthly_income += h.get_monthly_income()
    monthly_income = new_monthly_income + cash*ETF_YRLY_DRAW/MONTHS_IN_YEAR
    
    print("\n")
    print("CASH: " + str(cash))
    print("MOS: " + str(months))
    print("MONTHLY: " + str(monthly_income))
    print("\n")
    
    


