import requests
from web3 import Web3, HTTPProvider

APIKEY='...'
INFURAKEY='...'

w3 = Web3(HTTPProvider('https://ropsten.infura.io/' + INFURAKEY))

def sendETH (fromAddress, toAddress, weiValue, weiGasPrice, fromWIF ):
    """Send testnet Ether from `fromAddress` to `toAddress`.

    Args:
        fromAddress (str): Address of sender.
        toAddress (str): Address of recipient.
        weiValue (int): Transaction amount in Wei.
            Pass -1 to send entire balance.
        weiGasPrice (int): Gas price in Wei.
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
        if len(fromAddress) != 42:
            response['error'] = "fromAddress should be 34 letters."
            return response
        if len(toAddress) != 42:
            response['error'] = "toAddress should be 34 letters."
            return response
        if len(fromWIF) != 64:
            response['error'] = "fromWIF should be 52 letters."
            return response

        account = w3.eth.account.from_key(fromWIF);

        if account.address != fromAddress:
            response['error'] = "fromAddress cannot be derived from fromWIF."
            return response

        weiBalance = w3.eth.getBalance(fromAddress)
        print ('\nBalance (wei): ')
        print (weiBalance)

        txInfo = {
            'nonce': w3.eth.getTransactionCount(fromAddress),
            'gasPrice': weiGasPrice, # w3.eth.gasPrice
            'gas': 21000,
            'to': toAddress,
            'value': 0
        }

        weiFee = txInfo['gasPrice'] * txInfo['gas']

        if weiValue == -1: # sending all amount
            if weiBalance < weiFee:
                response['error'] = "insufficient balance. less than tx fee."
                return response
            else:
                txInfo['value'] = weiBalance - weiFee
        else:
            if weiBalance < weiFee + weiValue:
                response['error'] = "insufficient balance."
                return response
            else:
                txInfo['value'] = weiValue

        signedTx = w3.eth.account.sign_transaction(txInfo, fromWIF)

        result = w3.eth.sendRawTransaction(signedTx.rawTransaction)

        # print((signedTx.rawTransaction.hex())[2:]) # remove '0x'

        # decodedTx = requests.post(
        #     url='https://api.blockcypher.com/v1/eth/main/txs/push?token=' + APIKEY,
        #     data={
        #         'tx': (signedTx.rawTransaction.hex())[2:]
        #     }
        # )

        response['status'] = 'success'
        response['result'] = result.hex()
        return response
    except TypeError as err:
        response['error'] = str(err)
        return response
    except Exception as err:
        response['error'] = str(err)
        return response
    response['error'] = 'unexpected error occured.'
    return response

result = sendETH (
    '0xCd087f128D471606584B1DD9A46981dD362beae9',
    '0x1398c7d06E83C00697eE8B1e004619be7f7F0d62',
    1234500000000000,
    2448764346,
    '9c686f0833d54a6c31a23ade0ae4e280e1b4eed575b31e769343e2e20f93b418'
)

print ('\nResult: ')
print (result)

'''
WIF: 
05ed62307da473349e8c148df52d4181fe1714d004dbfe465e4d7394d3985a02
Address: 
0x1398c7d06E83C00697eE8B1e004619be7f7F0d62

WIF: 
9c686f0833d54a6c31a23ade0ae4e280e1b4eed575b31e769343e2e20f93b418
Address: 
0xCd087f128D471606584B1DD9A46981dD362beae9
'''
