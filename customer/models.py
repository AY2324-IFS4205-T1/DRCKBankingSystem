from decimal import Decimal
import uuid

from django.core.validators import RegexValidator
from django.db import models

from user.models import User


# Create your models here.
class Customer(models.Model):
    class Meta:
        db_table = 'customer"."customer_info'

    class Gender(models.TextChoices):
        FEMALE = "F"
        MALE = "M"
    
    class Nationalities(models.TextChoices):
        Afghans = "Afghans"
        Albanians = "Albanians"
        Algerians = "Algerians"
        Americans = "Americans"
        Andorrans = "Andorrans"
        Angolans = "Angolans"
        Antiguans_and_Barbudans = "Antiguans_and_Barbudans"
        Argentines = "Argentines"
        Armenians = "Armenians"
        Arubans = "Arubans"
        Australians = "Australians"
        Austrians = "Austrians"
        Azerbaijanis = "Azerbaijanis"
        Bahamians = "Bahamians"
        Bahrainis = "Bahrainis"
        Bangladeshis = "Bangladeshis"
        Barbadians = "Barbadians"
        Basques = "Basques"
        Belarusians = "Belarusians"
        Belgians = "Belgians"
        Belizeans = "Belizeans"
        Beninese = "Beninese"
        Bermudians = "Bermudians"
        Bhutanese = "Bhutanese"
        Bolivians = "Bolivians"
        Bosniaks = "Bosniaks"
        Bosnians_and_Herzegovinians = "Bosnians_and_Herzegovinians"
        Botswana = "Botswana"
        Brazilians = "Brazilians"
        Bretons = "Bretons"
        British = "British"
        British_Virgin_Islanders = "British_Virgin_Islanders"
        Bruneians = "Bruneians"
        Bulgarians = "Bulgarians"
        Macedonian_Bulgarians = "Macedonian_Bulgarians"
        Burkinabés = "Burkinabés"
        Burmese = "Burmese"
        Burundians = "Burundians"
        Cambodians = "Cambodians"
        Cameroonians = "Cameroonians"
        Canadians = "Canadians"
        Catalans = "Catalans"
        Cape_Verdeans = "Cape_Verdeans"
        Caymanians = "Caymanians"
        Chaldeans = "Chaldeans"
        Chadians = "Chadians"
        Chileans = "Chileans"
        Chinese = "Chinese"
        Colombians = "Colombians"
        Comorians = "Comorians"
        Congolese = "Congolese"
        Costa_Ricans = "Costa_Ricans"
        Croats = "Croats"
        Cubans = "Cubans"
        Cypriots = "Cypriots"
        Czechs = "Czechs"
        Danes = "Danes"
        Greenlanders = "Greenlanders"
        Djiboutians = "Djiboutians"
        Dominicans = "Dominicans"
        Dutch = "Dutch"
        East_Timorese = "East_Timorese"
        Ecuadorians = "Ecuadorians"
        Egyptians = "Egyptians"
        Emiratis = "Emiratis"
        English = "English"
        Equatoguineans = "Equatoguineans"
        Eritreans = "Eritreans"
        Estonians = "Estonians"
        Ethiopians = "Ethiopians"
        Falkland_Islanders = "Falkland_Islanders"
        Faroese = "Faroese"
        Fijians = "Fijians"
        Finns = "Finns"
        Finnish_Swedish = "Finnish_Swedish"
        Filipinos = "Filipinos"
        French_citizens = "French_citizens"
        Gabonese = "Gabonese"
        Gambians = "Gambians"
        Georgians = "Georgians"
        Germans = "Germans"
        Baltic_Germans = "Baltic_Germans"
        Ghanaians = "Ghanaians"
        Gibraltarians = "Gibraltarians"
        Greeks = "Greeks"
        Greek_Macedonians = "Greek_Macedonians"
        Grenadians = "Grenadians"
        Guatemalans = "Guatemalans"
        Guianese = "Guianese"
        Guineans = "Guineans"
        Guinea_Bissau_nationals = "Guinea_Bissau_nationals"
        Guyanese = "Guyanese"
        Haitians = "Haitians"
        Hondurans = "Hondurans"
        Hong_Kongers = "Hong_Kongers"
        Hungarians = "Hungarians"
        Icelanders = "Icelanders"
        I_Kiribati = "I_Kiribati"
        Indians = "Indians"
        Indonesians = "Indonesians"
        Iranians = "Iranians"
        Iraqis = "Iraqis"
        Irish = "Irish"
        Israelis = "Israelis"
        Italians = "Italians"
        Ivoirians = "Ivoirians"
        Jamaicans = "Jamaicans"
        Japanese = "Japanese"
        Jordanians = "Jordanians"
        Kazakhs = "Kazakhs"
        Kenyans = "Kenyans"
        Kosovars = "Kosovars"
        Kuwaitis = "Kuwaitis"
        Kyrgyzs = "Kyrgyzs"
        Lao = "Lao"
        Latvians = "Latvians"
        Lebanese = "Lebanese"
        Liberians = "Liberians"
        Libyans = "Libyans"
        Liechtensteiners = "Liechtensteiners"
        Lithuanians = "Lithuanians"
        Luxembourgers = "Luxembourgers"
        Macao = "Macao"
        Macedonians = "Macedonians"
        Malagasy = "Malagasy"
        Malawians = "Malawians"
        Malaysians = "Malaysians"
        Maldivians = "Maldivians"
        Malians = "Malians"
        Maltese = "Maltese"
        Manx = "Manx"
        Marshallese = "Marshallese"
        Mauritanians = "Mauritanians"
        Mauritians = "Mauritians"
        Mexicans = "Mexicans"
        Micronesians = "Micronesians"
        Moldovans = "Moldovans"
        Monégasque = "Monégasque"
        Mongolians = "Mongolians"
        Montenegrins = "Montenegrins"
        Moroccans = "Moroccans"
        Mozambicans = "Mozambicans"
        Namibians = "Namibians"
        Nauruans = "Nauruans"
        Nepalese = "Nepalese"
        New_Zealanders = "New_Zealanders"
        Nicaraguans = "Nicaraguans"
        Nigeriens = "Nigeriens"
        Nigerians = "Nigerians"
        Norwegians = "Norwegians"
        Omani = "Omani"
        Pakistanis = "Pakistanis"
        Palauans = "Palauans"
        Palestinians = "Palestinians"
        Panamanians = "Panamanians"
        Papua_New_Guineans = "Papua_New_Guineans"
        Paraguayans = "Paraguayans"
        Peruvians = "Peruvians"
        Poles = "Poles"
        Portuguese = "Portuguese"
        Puerto_Ricans = "Puerto_Ricans"
        Qatari = "Qatari"
        Quebecers = "Quebecers"
        Réunionnais = "Réunionnais"
        Romanians = "Romanians"
        Russians = "Russians"
        Baltic_Russians = "Baltic_Russians"
        Rwandans = "Rwandans"
        Saint_Kitts_and_Nevis = "Saint_Kitts_and_Nevis"
        Saint_Lucians = "Saint_Lucians"
        Salvadorans = "Salvadorans"
        Sammarinese = "Sammarinese"
        Samoans = "Samoans"
        Saudis = "Saudis"
        Scots = "Scots"
        Senegalese = "Senegalese"
        Serbs = "Serbs"
        Seychellois = "Seychellois"
        Sierra_Leoneans = "Sierra_Leoneans"
        Singaporean = "Singaporean"
        Slovaks = "Slovaks"
        Slovenes = "Slovenes"
        Solomon_Islanders = "Solomon_Islanders"
        Somalis = "Somalis"
        Somalilanders = "Somalilanders"
        Sotho = "Sotho"
        South_Africans = "South_Africans"
        Spaniards = "Spaniards"
        Sri_Lankans = "Sri_Lankans"
        Sudanese = "Sudanese"
        Surinamese = "Surinamese"
        Swazi = "Swazi"
        Swedes = "Swedes"
        Swiss = "Swiss"
        Syriacs = "Syriacs"
        Syrians = "Syrians"
        Taiwanese = "Taiwanese"
        Tamils = "Tamils"
        Tajik = "Tajik"
        Tanzanians = "Tanzanians"
        Thais = "Thais"
        Tibetans = "Tibetans"
        Tobagonians = "Tobagonians"
        Togolese = "Togolese"
        Tongans = "Tongans"
        Trinidadians = "Trinidadians"
        Tunisians = "Tunisians"
        Turks = "Turks"
        Tuvaluans = "Tuvaluans"
        Ugandans = "Ugandans"
        Ukrainians = "Ukrainians"
        Uruguayans = "Uruguayans"
        Uzbeks = "Uzbeks"
        Vanuatuans = "Vanuatuans"
        Venezuelans = "Venezuelans"
        Vietnamese = "Vietnamese"
        Vincentians = "Vincentians"
        Welsh = "Welsh"
        Yemenis = "Yemenis"
        Zambians = "Zambians"
        Zimbabweans = "Zimbabweans"

    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    identity_no = models.CharField(max_length=9, validators=[RegexValidator(regex='^[STFG][0-9]{7}[A-Z]$', message='Invalid Identity Number')])
    address = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=6, validators=[RegexValidator(regex='^[0-9]{6}$', message='Invalid postal code')])
    nationality = models.CharField(max_length=30, choices=Nationalities.choices)
    gender = models.CharField(max_length=1, choices=Gender.choices)


class AccountTypes(models.Model):
    class Meta:
        db_table = 'customer"."account_types'

    type = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)


class Accounts(models.Model):
    class Meta:
        db_table = 'customer"."accounts'
    
    class AccountStatus(models.TextChoices):
        ACTIVE = "A"
        PENDING = "P"
        CLOSED = "C"

    account = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    type = models.ForeignKey(AccountTypes, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    status = models.CharField(max_length=1, choices=AccountStatus.choices)
    date_created = models.DateTimeField(auto_now_add=True)


class Transactions(models.Model):    
    class Meta:
        db_table = 'customer"."transactions'
    
    class TransactionTypes(models.TextChoices):
        DEPOSIT = "D"
        WITHDRAWAL = "W"
        TRANSFER = "T"
    
    transaction = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_type = models.CharField(max_length=1, choices=TransactionTypes.choices)
    sender = models.ForeignKey(Accounts, related_name='sent_transactions', on_delete=models.CASCADE, null=True)
    recipient = models.ForeignKey(Accounts, related_name='received_transactions', on_delete=models.CASCADE, null=True)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    
    # Will review this another day
    # def clean_account(self):
    #     if self.sender_id == self.recipient_id:
    #         raise ValueError("Sender account should not be recipient account")
    # def clean_amount(self):
    #     if self.type in ['W'] and self.amount > self.sender_id.balance:
    #         raise ValueError("Withdrawal amount is too much")
    #     elif self.type in ['T'] and self.amount > self.sender_id.balance:
    #         raise ValueError("Transfer amount is too much")
