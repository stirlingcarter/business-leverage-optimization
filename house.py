import uuid
import itertools
MONTHS_IN_YEAR = 12

### FINANCIAL STARTING POINT
SUPPLEMENTAL_INC_PER_MO = 2000
MOS_SI_REC = 36
STARTING_CASH = 25000

### USER CHOICE PARAMS

# dynamic
HOME_VALUE_TARGET = 160000 # 0
MAX_HOUSES = 7 # 1
REFI_CASH_MIN = 10000 # 2
REFI_MOS_MIN = 12 # 3

#[point],[ra,nge]
DEFAULT_SNAPSHOT = [HOME_VALUE_TARGET,MAX_HOUSES,REFI_CASH_MIN,REFI_MOS_MIN]

# static
MIN_PURCHASE_GAP_MOS = 10
REFI = 1 # 1 is true
PAYOFF = 0 # 1 is true

### RENT ADJUSTMENT PARAMS
ADJUST_RENT_TO_MARKET = "ON_TURNOVER"
RENT_ADJUST_PERIOD_MOS = 12 #PERIODICLY
AVG_TURNOVER_MOS = 50 #ON_TURNOVER

### MORTGAGE PARAMS
MORTGAGE_LENGTHS = 30
RI_YRLY_APPR = .03
ETF_YRLY_DRAW = .04
APR = .03
APR_FACTOR = 1.93
DOWN_PAYMENT_PERCENTAGE = .2
GENERAL_DOWN = DOWN_PAYMENT_PERCENTAGE * HOME_VALUE_TARGET

### PROPERTY OPS
RENT_PER_VALUE = .01
CAPEX_PER_RENT = .10
MAINT_PER_RENT = .10
MANAGEMENT_PER_RENT = .10
VACANCY_PER_RENT = .05
INSURANCE_PER_VALUE_PER_MO = .018 / MONTHS_IN_YEAR
PROPERTY_TAX_PER_VALUE_PER_MO = .0136 / MONTHS_IN_YEAR

### LIMITS
TARGET_MO_INC = 1000
MAX_YEARS = 30

class House:

    def __init__(self, cost, down):
        self.mo_since_last_refi = 0
        self.appr_value = cost
        self.initial_value = cost
        self.rent = self.initial_value * RENT_PER_VALUE
        self.equity = down
        self.age_months = 0
        self.p_owed = cost - down
        total_owed = self.p_owed + self.p_owed/APR_FACTOR
        self.i_owed = total_owed - self.p_owed
        self.MONTHLY = total_owed/MONTHS_IN_YEAR/MORTGAGE_LENGTHS
        self.NOI = self.getNOI()

        
    #a monthly step
    def step(self):
    
        #age
        self.age_months += 1
        #adjust rent
        if  ADJUST_RENT_TO_MARKET == "ON_TURNOVER" and self.age_months % AVG_TURNOVER_MOS == 0:
            self.rent = self.appr_value * RENT_PER_VALUE
        elif ADJUST_RENT_TO_MARKET == "PERIODICLY" and self.age_months % RENT_ADJUST_PERIOD_MOS == 0:
            self.rent = self.appr_value * RENT_PER_VALUE
            
        #calculate and adjust p and i
        if self.equity < self.initial_value:
            interest = APR/MONTHS_IN_YEAR*self.p_owed
            principal = self.MONTHLY - interest
            self.p_owed -= principal
            self.equity += principal
            self.i_owed -= interest
        #acct for apr
        self.appr_value *= (1 + (RI_YRLY_APPR/MONTHS_IN_YEAR))#.04 is yrly RI ^
        
            
    
    def getNOI(self):
    
        NOI = self.rent
        NOI -= self.rent * CAPEX_PER_RENT
        NOI -= self.rent * VACANCY_PER_RENT
        NOI -= self.rent * MAINT_PER_RENT
        NOI -= self.rent * MANAGEMENT_PER_RENT
        NOI -= self.appr_value * PROPERTY_TAX_PER_VALUE_PER_MO
        NOI -= self.appr_value * INSURANCE_PER_VALUE_PER_MO
        
        if self.equity < self.initial_value:
            NOI -= self.MONTHLY
        return NOI
        
    def get_monthly_income(self):
        if self.age_months % MONTHS_IN_YEAR == 0:
            self.NOI = self.getNOI()
        return self.NOI
    
    def print_house(self):
        print("\n")
        print("RED: " + str(round(self.getRed(),2)) + "% of current value, or $" + str(self.p_owed))
        print("VALUE: " + str(self.appr_value))
        print("BRINGIN IN MONTHLY: " + str(self.get_monthly_income()))
        print("\n")
        
    def resetMosSinceLastREFI(self):
        self.mo_since_last_refi = 0
            
    def incMosSinceLastREFI(self):
        self.mo_since_last_refi += 1
    
    
    
    def refi(self):
        down = self.appr_value * DOWN_PAYMENT_PERCENTAGE
        out = self.appr_value - self.initial_value + self.equity - down
        self.initial_value = self.appr_value
        cash_loan_out = self.appr_value - down
        self.equity = down
        self.p_owed = cash_loan_out
        total_owed = self.p_owed + self.p_owed/APR_FACTOR
        self.i_owed = total_owed - self.p_owed
        self.MONTHLY = total_owed/MONTHS_IN_YEAR/MORTGAGE_LENGTHS
        return out
        
    def payOff(self):
        owed = self.p_owed
        self.p_owed = 0
        self.equity = self.initial_value
        return owed
    
    def getGreen(self):
        green = self.appr_value - self.p_owed
        return 100 - self.getRed()
        
    def getRed(self):
        if self.equity >= self.initial_value:
            return 0
        else:
            return 100 / self.appr_value * self.p_owed

def getRanges(snapshot):
    ranges = []
    for p in range(len(snapshot)):
        expanded_range = []
        r = snapshot[p] #[4,3,5]
        
        if len(r) == 1:
            expanded_range = r # [4]
            ranges.append(expanded_range)
        else:
            if len(r) == 2:
                r.append(1)
            for n in range(r[0],r[1],r[2]):
                expanded_range.append(n)
            ranges.append(expanded_range)
            
    return ranges
        
def getOptimum(snapshot_ranges):
    ranges = getRanges(snapshot_ranges)
    optimum_snapshot = []
    optimum_time_mos = 100000000
    optimum_uuid = 0

    # for [4,5,6],[3],[5,10],[1]
    for point in itertools.product(ranges[0], ranges[1], ranges[2], ranges[3]):
        SNAPSHOT = [point[0],point[1],point[0] * DOWN_PAYMENT_PERCENTAGE,point[3]]
        ans_set = run(SNAPSHOT)
        time_mos = ans_set[0]
        u = ans_set[1]
        if time_mos < optimum_time_mos:
            optimum_snapshot = SNAPSHOT
            optimum_time_mos = time_mos
            optimum_uuid = u
    
    ans = {}
    ans["optimum_snapshot"] = optimum_snapshot
    ans["optimum_time_mos"] = optimum_time_mos
    ans["optimum_uuid"] = optimum_uuid

 
    return ans
        
def run(SNAPSHOT):
    HOME_VALUE_TARGET = SNAPSHOT[0] # 0
    MAX_HOUSES = SNAPSHOT[1] # 1
    REFI_CASH_MIN = SNAPSHOT[2] # 2
    REFI_MOS_MIN = SNAPSHOT[3] # 3
    
    u = str(uuid.uuid1()).split("-")[0]
    print(u)


    cash = STARTING_CASH
    monthly_income = 0
    houses = []
    months = 0
    mos_since_last_purchase = MIN_PURCHASE_GAP_MOS+1
    months_target_met = 30000
    time_set = False
    while (monthly_income < TARGET_MO_INC or months < MAX_YEARS * MONTHS_IN_YEAR) and cash > 0:
        
        if months < MOS_SI_REC:
            cash += SUPPLEMENTAL_INC_PER_MO
        months += 1


        down = HOME_VALUE_TARGET * DOWN_PAYMENT_PERCENTAGE

        for h in houses:
            h.step()
            
        #REFI
        if REFI == 1:
            for h in houses:
                down = h.appr_value * DOWN_PAYMENT_PERCENTAGE
                out = h.appr_value - h.initial_value + h.equity - down
                if out > REFI_CASH_MIN and len(houses) < MAX_HOUSES and h.mo_since_last_refi >= REFI_MOS_MIN:
                    print("\n\n\nREFIIIIIII\n\n")
                    h.resetMosSinceLastREFI()
                    cash += h.refi()
                else:
                    h.incMosSinceLastREFI()

        #PAYOFF
        if PAYOFF == 1 and len(houses) == MAX_HOUSES:
            for h in houses:
                if h.p_owed != 0 and h.p_owed < cash:
                    print("PAID OFF")
                cash -= h.payOff()

        cash += monthly_income
        
        new_monthly_income = 0
        
        
        
        mos_since_last_purchase += 1
        if cash > down and len(houses) < MAX_HOUSES and mos_since_last_purchase >= MIN_PURCHASE_GAP_MOS:
            print("PURCHASED")

            houses.append(House(HOME_VALUE_TARGET,down))
            cash -= down
            mos_since_last_purchase = 0
        for h in houses:
            new_monthly_income += h.get_monthly_income()
            
        monthly_income = new_monthly_income + cash*ETF_YRLY_DRAW/MONTHS_IN_YEAR
        
        
        if monthly_income > TARGET_MO_INC:
            if time_set == False:
                print(months_target_met)
                months_target_met = months
                print(months_target_met)
                time_set = True
            
        print("\n")
        print("CASH: " + str(cash))
        print("MOS: " + str(months))
        print("MONTHLY: " + str(monthly_income))
        print("\n")
        
            

        
        if months%MONTHS_IN_YEAR == 0:
            print("----------------------------------------------------------------------VVV-YEAR" + str(months//MONTHS_IN_YEAR)+"-VVV--------------------------------------------------------------")
            for i in range(len(houses)):
                print("\n")
                print("HOUSE " + str(i) + ":")
                houses[i].print_house()
            print("--------------------------------------" + u + "-------------------------------^^^-YEAR"+str(months//MONTHS_IN_YEAR)+"-^^^------------------------------------------------------------")
        
    if cash <= 0:
        print("YA LOSE")


    print("----------------------------------------------------------------------VVV-FINAL-VVV--------------------------------------------------------------")
    for i in range(len(houses)):
        print("\n")
        print("HOUSE " + str(i) + ":")
        houses[i].print_house()
    print("-----------------------------------------------" + u + "----------------------^^^-FINAL-^^^------------------------------------------------------------")
    
    return [months_target_met, u]
    












###         HOME_VALUE_TARGET,MAX_HOUSES,REFI_CASH_MIN,REFI_MOS_MIN

snapshot_ranges = [[75000,500000,10000],[1,5],[GENERAL_DOWN],[MONTHS_IN_YEAR]]

            
optimum = getOptimum(snapshot_ranges)
        
print("\n")
print("\n")
print("-----------------------------------FINAL RESULTS-----------------------------------")



print("OPTIMUM: " + str(optimum))

