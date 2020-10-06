import uuid
u = str(uuid.uuid1()).split("-")[0]
print(u)

MORTGAGE_LENGTHS = 30
APR = .03
APR_FACTOR = 1.93
HOME_VALUE_TARGET = 100000
DOWN_PAYMENT_PERCENTAGE = .2
RI_YRLY_APPR = .04
ETF_YRLY_DRAW = .04
MONTHS_IN_YEAR = 12
MAX_HOUSES = 10
ADJUST_RENT_TO_MARKET = "ON_TURNOVER" #ON_TURNOVER or PERIODICLY
RENT_ADJUST_PERIOD_MOS = -1
AVG_TURNOVER_MOS = 50
RENT_AS_PERCENTAGE_OF_VALUE = .008
CAPEX_AS_PER_VALUE = .15



class House:

    def __init__(self, cost, down):
    
        self.initial_value = cost
        self.rent = self.initial_value * RENT_AS_PERCENTAGE_OF_VALUE
        self.age_months = 0
        self.appr_value = cost
        self.equity = down
        self.p_owed = cost - down
        total_owed = self.p_owed + self.p_owed/APR_FACTOR
        self.i_owed = total_owed - self.p_owed
        self.MONTHLY = total_owed/MONTHS_IN_YEAR/MORTGAGE_LENGTHS
        
    #a monthly step
    def step(self):
    
        #age
        self.age_months += 1
        #adjust rent
        if  ADJUST_RENT_TO_MARKET == "ON_TURNOVER" and self.age_months % AVG_TURNOVER_MOS == 0:
            self.rent = self.appr_value * RENT_AS_PERCENTAGE_OF_VALUE
        elif ADJUST_RENT_TO_MARKET == "PERIODICLY" and self.age_months % RENT_ADJUST_PERIOD_MOS == 0:
            self.rent = self.appr_value * RENT_AS_PERCENTAGE_OF_VALUE
            
        #calculate and adjust p and i
        if self.equity < self.initial_value:
            interest = APR/MONTHS_IN_YEAR*self.p_owed
            principal = self.MONTHLY - interest
            self.p_owed -= principal
            self.equity += principal
            self.i_owed -= interest
        #acct for apr
        self.appr_value *= (1 + (RI_YRLY_APPR/MONTHS_IN_YEAR))#.04 is yrly RI ^
        
    def get_monthly_income(self):
        NOI = self.rent - self.rent * CAPEX_AS_PER_VALUE
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
        self.initial_value = self.appr_value
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
    
    

print(u)
