import * as React from 'react';
import {
  Callout,
  CalloutIcon,
  CalloutText,
  CalloutProps,
} from '@/components/ui/callout';

export type CalloutObject = {
  state: boolean;
  message: string;
};

export interface CustomCalloutProps extends CalloutProps {
  iconChildren?: React.ReactNode;
  textChildren?: React.ReactNode;
}

export const CustomCallout: React.FC<CustomCalloutProps> = ({
  variant,
  icon,
  iconChildren,
  textChildren,
  children,
  ...props
}) => {
  return (
    <Callout variant={variant} {...props}>
      {icon && <CalloutIcon>{icon}</CalloutIcon>}
      {iconChildren && <CalloutIcon>{iconChildren}</CalloutIcon>}
      {textChildren && <CalloutText>{textChildren}</CalloutText>}
      {children}
    </Callout>
  );
};

export default CustomCallout;
