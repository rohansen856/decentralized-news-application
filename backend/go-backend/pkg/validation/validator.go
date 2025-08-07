package validation

import (
	"fmt"
	"reflect"
	"strings"

	"github.com/go-playground/validator/v10"
)

type Validator struct {
	validate *validator.Validate
}

func NewValidator() *Validator {
	v := validator.New()
	
	v.RegisterTagNameFunc(func(fld reflect.StructField) string {
		name := strings.SplitN(fld.Tag.Get("json"), ",", 2)[0]
		if name == "-" {
			return ""
		}
		return name
	})

	return &Validator{validate: v}
}

func (v *Validator) Validate(i interface{}) error {
	return v.validate.Struct(i)
}

func (v *Validator) FormatValidationErrors(err error) map[string]string {
	errors := make(map[string]string)
	
	if validationErrors, ok := err.(validator.ValidationErrors); ok {
		for _, fieldError := range validationErrors {
			fieldName := fieldError.Field()
			
			switch fieldError.Tag() {
			case "required":
				errors[fieldName] = fmt.Sprintf("%s is required", fieldName)
			case "email":
				errors[fieldName] = fmt.Sprintf("%s must be a valid email address", fieldName)
			case "min":
				errors[fieldName] = fmt.Sprintf("%s must be at least %s characters long", fieldName, fieldError.Param())
			case "max":
				errors[fieldName] = fmt.Sprintf("%s must not exceed %s characters", fieldName, fieldError.Param())
			case "uuid":
				errors[fieldName] = fmt.Sprintf("%s must be a valid UUID", fieldName)
			default:
				errors[fieldName] = fmt.Sprintf("%s is invalid", fieldName)
			}
		}
	}
	
	return errors
}