# bond-pricing


> a bond is a type of security under which the issuer (debtor) owes the holder (creditor) a debt, and is obliged – depending on the terms – to provide cash flow to the creditor (e.g. repay the principal (i.e. amount borrowed) of the bond at the maturity date as well as interest (called the coupon) over a specified amount of time)

The main characteristics of a bond are its maturity date and its coupon. We can ignore coupon frequency and day count convention which only have second order effects.
#### Bond valuation
As often in finance the valuation of bond comes down to discounting future cash flows. The actual discounting requires an interest rate that we'll assume to be constant for simplicity. The cash flows depend on two credit parameters: the default probability and the recovery rate. In the absence of default, the issuer will pay coupons on a regular basis and pay back the notional on maturity date. In case of the default, the holder will receive recovery rate times the face value of the bond only. The default probability at time t depends on t and the default intensity spread divided by (1 - recovery)
