// Copyright (c)  The Bitcoin Core developers
// Copyright (c) 2017 The Raven Core developers
// Copyright (c) 2018 The Rito Core developers
// Copyright (c) 2019 The Naldcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef NALD_QT_NALDADDRESSVALIDATOR_H
#define NALD_QT_NALDADDRESSVALIDATOR_H

#include <QValidator>

/** Base58 entry widget validator, checks for valid characters and
 * removes some whitespace.
 */
class NaldcoinAddressEntryValidator : public QValidator
{
    Q_OBJECT

public:
    explicit NaldcoinAddressEntryValidator(QObject *parent);

    State validate(QString &input, int &pos) const;
};

/** Naldcoin address widget validator, checks for a valid nald address.
 */
class NaldcoinAddressCheckValidator : public QValidator
{
    Q_OBJECT

public:
    explicit NaldcoinAddressCheckValidator(QObject *parent);

    State validate(QString &input, int &pos) const;
};

#endif // NALD_QT_NALDADDRESSVALIDATOR_H
