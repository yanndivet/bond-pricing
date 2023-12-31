# bond-pricing


> a bond is a type of security under which the issuer (debtor) owes the holder (creditor) a debt, and is obliged – depending on the terms – to provide cash flow to the creditor (e.g. repay the principal (i.e. amount borrowed) of the bond at the maturity date as well as interest (called the coupon) over a specified amount of time)

The main characteristics of a bond are its maturity date and its coupon. As a first order approximation, we can ignore coupon frequency and day count convention which only have second order effects.

#### Bond valuation
As often in finance the valuation of bond comes down to discounting future cash flows. The actual discounting requires an interest rate that we'll assume to be constant for simplicity. The cash flows depend on two [credit](https://en.wikipedia.org/wiki/Credit) parameters: 
* [the probability of default](https://en.wikipedia.org/wiki/Probability_of_default) 
* and the recovery rate, sometimes also referred to as [Loss Given Default (LGD)](https://en.wikipedia.org/wiki/Loss_given_default) 

In the absence of [default](https://en.wikipedia.org/wiki/Default_(finance)), the issuer will pay coupons on a regular basis and pay back the notional on maturity date. In case of the default, the holder will receive recovery rate times the face value of the bond only. The default probability at time t depends on t and the default intensity spread divided by (1 - recovery)

There are two main approaches to model credit risk, that is estimate the survival probabilty over time:
* The [reduced-form approach](https://en.wikipedia.org/wiki/Jarrow%E2%80%93Turnbull_model), which focuses on modeling default probabilities as stochastic processes
* The structural approach in which bankruptcy is modeled from the firm’s asset value. The approch is also known as firm value model or [Merton model](https://en.wikipedia.org/wiki/Merton_model)

Here we only look at the first approach and assumes for sake of simplicity that both credit spread and interest are constant over time, in which case the reduced-form model gives closed form formula, which can easily be vectorized in python using numpy. Sensitivities are computed using finite difference method rather than by deriving the close form formula giving the price of bond.
