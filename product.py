#This file is part product_training module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, Bool
from trytond.transaction import Transaction
from trytond.model.fields import depends

__all__ = ['Template', 'Product']
__metaclass__ = PoolMeta


class Template:
    __name__ = "product.template"
    training = fields.Boolean('Training', states={
            'readonly': ~Eval('active', True),
            }, depends=['active'])
    training_sessions = fields.Function(fields.One2Many('product.product', None,
            'Sessions'), 'get_training_sessions')

    def get_training_sessions(self, name):
        '''Get current sessions (start date =< today)'''
        Date = Pool().get('ir.date')
        if not self.training:
            return []

        products = set()
        for product in self.products:
            if product.training_start_date >= Date.today():
                products.add(product.id)
        return list(products)


class Product:
    __name__ = 'product.product'
    training = fields.Function(fields.Boolean('Training'), 'get_training')
    training_start_date = fields.Date('Start Date',
        states={
            'required': Bool(Eval('training')),
            },
        depends=['training'])
    training_end_date = fields.Date('End Date',
        states={
            'required': Bool(Eval('training')),
            },
        depends=['training'])
    training_registration = fields.Date('Registration Date',
        states={
            'required': Bool(Eval('training')),
            },
        depends=['training'],
        help='Last day to registration')
    training_place = fields.Many2One('party.address', 'Place')
    training_seats = fields.Integer('Seats')
    training_extra = fields.Char('Extra', translate=True)

    def get_training(self, name):
        return self.template.training if self.template else False

    def get_rec_name(self, name):
        if self.training_start_date:
            DATE_FORMAT = '%s' % (Transaction().context['locale']['date'])

            start_date = self.training_start_date.strftime(DATE_FORMAT)
            end_date = self.training_end_date.strftime(DATE_FORMAT)

            name = ''
            if self.code:
                name += '[' + self.code + '] '
            name += self.name + ' (' + str(start_date) + ' - ' + str(end_date) + ')'
            return name
        else:
            return super(Product, self).get_rec_name(name)

    @depends('training_start_date', 'training_registration', 'training_end_date')
    def on_change_training_start_date(self):
        res = {}
        if not self.training_end_date and self.training_start_date:
            res['training_end_date'] = self.training_start_date
        if not self.training_registration and self.training_start_date:
            res['training_registration'] = self.training_start_date
        return res
