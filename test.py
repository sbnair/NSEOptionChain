
r= 'red'
x = 25/100*100
print(f'background : linear-gradient(90deg,{r} {x}%, transparent {x}%)')

# import pandas as pd
# import numpy as np


# def highlight_max(x):
#     a = x.max()
#     print(a)
#     return ['background-color: yellow' if v == x.max() else ''
#                 for v in x]

# df = pd.DataFrame(np.random.randn(5, 3))
# with open ('out.html','w') as out:
#     out.write(df.style.apply(highlight_max).render())


'''
np.random.seed(24)
df = pd.DataFrame({'A': np.linspace(1, 10, 10)})
df = pd.concat([df, pd.DataFrame(np.random.randn(10, 4), 
columns=list('BCDE'))],axis=1)
df.iloc[0, 2] = np.nan

def highlight_greater(x):
    r = 'red'
    g = 'gray'

    m1 = x['B'] > x['C']
    m2 = x['D'] > x['E']

    df1 = pd.DataFrame('background-color: ', index=x.index, columns=x.columns)
    #rewrite values by boolean masks
    df1['B'] = np.where(m1, 'background-color: {}'.format(r), df1['B'])
    df1['D'] = np.where(m2, 'background-color: {}'.format(g), df1['D'])
    return df1

with open ('out.html','w') as out:
    out.write(df.style.apply(highlight_greater, axis=None).render())
'''

'''
def highlight_greater(row):

    color=""
    if row['B'] > row['C']:
       color = 'red'
    elif row['D'] > row['E']:
        color = 'gray'

    background = ['background-color: {}'.format(color) for _ in row]
    return background

with open ('out.html','w') as out:
    out.write(df.style.apply(highlight_greater, axis=1).render())
'''