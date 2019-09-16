from bit import PrivateKey, PrivateKeyTestnet
import blockcypher

APIKEY='...'

def sendBTC (fromAddress, toAddress, satValue, satFee, fromWIF ):
    """Send testnet Bitcoin from `fromAddress` to `toAddress`.

    Args:
        fromAddress (str): Address of sender.
        toAddress (str): Address of recipient.
        satValue (int): Transaction amount in Satoshi.
            Pass -1 to send entire balance.
        satFee (int): Transaction fee in Satoshi.
        fromWIF (str): WIF string of sender.

    Returns:
        Success:
            {
                'status': 'success',
                'result': decoded transaction
            }
        Failure:
            {
                'status': 'failure',
                'error': error message
            }
    """
    response = {
        'status': 'failure',
    }
    try:
        # validation
        if len(fromAddress) != 34:
            response['error'] = "fromAddress should be 34 letters."
            return response
        if len(toAddress) != 34:
            response['error'] = "toAddress should be 34 letters."
            return response
        if len(fromWIF) != 52:
            response['error'] = "fromWIF should be 52 letters."
            return response

        key = PrivateKeyTestnet(wif=fromWIF)
        if key.address != fromAddress:
            response['error'] = "fromAddress cannot be derived from fromWIF."
            return response

        key.get_balance(currency='satoshi')
        satBalance = key.balance
        print ('\nBalance (satoshi): ')
        print (satBalance)

        if satValue == -1: # sending all amount
            if satBalance < satFee:
                response['error'] = "insufficient balance. less than tx fee."
                return response
        else:
            if satBalance < satFee + satValue:
                response['error'] = "insufficient balance."
                return response

        # create transaction
        print ('\nTransactions: ')
        print (key.get_transactions())
        print ('\nUTXOs: ')
        print (key.get_unspents())

        if satValue == -1: # sending all amount
            rawtx = key.create_transaction(outputs=[], leftover=toAddress, fee=satFee, absolute_fee=True)
        else:
            output1 = (toAddress, satValue, 'satoshi')
            output2 = (fromAddress, satBalance - satValue - satFee, 'satoshi')
            rawtx = key.create_transaction(outputs=[output1, output2], fee=satFee, absolute_fee=True)

        # push transaction
        decodedTx = blockcypher.pushtx(tx_hex=rawtx, coin_symbol='btc-testnet', api_key=APIKEY)

        response['status'] = 'success'
        response['result'] = decodedTx

        return response
    except TypeError as err:
        response['error'] = str(err)
        return response
    except Exception as err:
        response['error'] = str(err)
        return response
    response['error'] = 'unexpected error occured.'
    return response

result = sendBTC (
    'mysZLCEAM5H46bp6Q6sbTLdrNV9tBjDVT9',
    'mpAandwtdkmdFStgp3hrSqo2yVrjGPCoLc',
    12345,
    2000,
    'cUhUgF3Qukk5y2GznCfQ8tXJUNDQjH3XC747RDEVoN3ADmmBqEaV'
)

print ('\nResult: ')
print (result)

'''
randomWif=None

randomPrivateKey = PrivateKeyTestnet(wif=randomWif)

print ('WIF: ')
print (randomPrivateKey.to_wif())

print ('Address: ')
print (randomPrivateKey.address)

WIF: 
cTrc22Vq2p6ETzt8yZjiUzHQ1rwKM2sRbzisghEvJvjV3osEPuyb
Address: 
mpAandwtdkmdFStgp3hrSqo2yVrjGPCoLc

WIF: 
cUhUgF3Qukk5y2GznCfQ8tXJUNDQjH3XC747RDEVoN3ADmmBqEaV
Address: 
mysZLCEAM5H46bp6Q6sbTLdrNV9tBjDVT9
'''
