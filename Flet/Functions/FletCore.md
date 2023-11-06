

### ft.Stack을 데이터로 받는 클래스
  - ft.UserControl

### ft.Control을 데이터로 받는 클래스
  - ft.AlertDialog
  - ft.AppBar
  - ft.ConstrainedControl
  - ft.DataColumn
  - ft.DataCell
  - ft.Page

### ft.ConstrainedControl을 데이터로 받는 클래스
  - ft.Card
  - ft.Column <- ScrollableControl을 데이터로도 받음
  - ft.Container
  - ft.ElevatedButton
  - ft.FletApp
  - ft.FloatingActionButton
  - ft.FoamFieldControl
  - ft.GestureDetector

### ft.Control이 받는 데이터
  - self,
  - ref: Optional[Ref] = None,
  - expand: Union[None, bool, int] = None,
  - col: Optional[ResponsiveNumber] = None,
  - opacity: OptionalNumber = None,
  - tooltip: Optional[str] = None,
  - visible: Optional[bool] = None,
  - disabled: Optional[bool] = None,
  - data: Any = None,

### ft.ConstrainedControl이 받는 데이터
   - self,
   - ref: Optional[Ref] = None,
   - expand: Union[None, bool, int] = None,
   - col: Optional[ResponsiveNumber] = None,
   - opacity: OptionalNumber = None,
   - tooltip: Optional[str] = None,
   - visible: Optional[bool] = None,
   - disabled: Optional[bool] = None,
   - data: Any = None,
   - key: Optional[str] = None,
   - width: OptionalNumber = None,
   - height: OptionalNumber = None,
   - left: OptionalNumber = None,
   - top: OptionalNumber = None,
   - right: OptionalNumber = None,
   - bottom: OptionalNumber = None,
   - rotate: RotateValue = None,
   - scale: ScaleValue = None,
   - offset: OffsetValue = None,
   - aspect_ratio: OptionalNumber = None,
   - animate_opacity: AnimationValue = None,
   - animate_size: AnimationValue = None,
   - animate_position: AnimationValue = None,
   - animate_rotation: AnimationValue = None,
   - animate_scale: AnimationValue = None,
   - animate_offset: AnimationValue = None,
   - on_animation_end=None,

### ft.Container가 받는 데이터

공통항목
  - self,
  - content: Optional[Control] = None,
  - ref: Optional[Ref] = None,
  - key: Optional[str] = None,
  - width: OptionalNumber = None,
  - height: OptionalNumber = None,
  - left: OptionalNumber = None,
  - top: OptionalNumber = None,
  - right: OptionalNumber = None,
  - bottom: OptionalNumber = None,
  - expand: Union[None, bool, int] = None,
  - col: Optional[ResponsiveNumber] = None,
  - opacity: OptionalNumber = None,
  - rotate: RotateValue = None,
  - scale: ScaleValue = None,
  - offset: OffsetValue = None,
  - aspect_ratio: OptionalNumber = None,
  - animate_opacity: AnimationValue = None,
  - animate_size: AnimationValue = None,
  - animate_position: AnimationValue = None,
  - animate_rotation: AnimationValue = None,
  - animate_scale: AnimationValue = None,
  - animate_offset: AnimationValue = None,
  - on_animation_end=None,
  - tooltip: Optional[str] = None,
  - visible: Optional[bool] = None,
  - disabled: Optional[bool] = None,
  - data: Any = None,

특화항목
  - padding: PaddingValue = None,
  - margin: MarginValue = None,
  - alignment: Optional[Alignment] = None,
  - bgcolor: Optional[str] = None,
  - gradient: Optional[Gradient] = None,
  - blend_mode: BlendMode = BlendMode.NONE,
  - border: Optional[Border] = None,
  - border_radius: BorderRadiusValue = None,
  - image_src: Optional[str] = None,
  - image_src_base64: Optional[str] = None,
  - image_repeat: Optional[ImageRepeat] = None,
  - image_fit: Optional[ImageFit] = None,
  - image_opacity: OptionalNumber = None,
  - shape: Optional[BoxShape] = None,
  - clip_behavior: Optional[ClipBehavior] = None,
  - ink: Optional[bool] = None,
  - animate: AnimationValue = None,
  - blur: Union[
            None, float, int, Tuple[Union[float, int], Union[float, int]], Blur
        ] = None,
  - shadow: Union[None, BoxShadow, List[BoxShadow]] = None,
  - url: Optional[str] = None,
  - url_target: Optional[str] = None,
  - theme: Optional[Theme] = None,
  - theme_mode: Optional[ThemeMode] = None,
  - on_click=None,
  - on_long_press=None,
  - on_hover=None,

### ft.Event 가 받는 데이터
  - self,
  - target: str, 
  - name: str, 
  - data: str

### ft.ControlEvent가 받는 데이터 <- ft.Event
  - self,
  - target: str, 
  - name: str, 
  - data: str, 
  - control, 
  - page

### ft.FilledButton이 받는 데이터 <- ft.ElevatedButton
  공통항목
  - self,
  - text: Optional[str] = None,
  - ref: Optional[Ref] = None,
  - key: Optional[str] = None,
  - width: OptionalNumber = None,
  - height: OptionalNumber = None,
  - expand: Union[None, bool, int] = None,
  - col: Optional[ResponsiveNumber] = None,
  - opacity: OptionalNumber = None,
  - tooltip: Optional[str] = None,
  - visible: Optional[bool] = None,
  - disabled: Optional[bool] = None,
  - data: Any = None,
  특화항목
  - icon: Optional[str] = None,
  - icon_color: Optional[str] = None,
  - style: Optional[ButtonStyle] = None,
  - content: Optional[Control] = None,
  - autofocus: Optional[bool] = None,
  - url: Optional[str] = None,
  - url_target: Optional[str] = None,
  - on_click=None,
  - on_long_press=None,
  - on_hover=None,

### ft.ElevatedButton이 받는 데이터
  공통항목
  - self,
  - text: Optional[str] = None,
  - ref: Optional[Ref] = None,
  - key: Optional[str] = None,
  - width: OptionalNumber = None,
  - height: OptionalNumber = None,
  - left: OptionalNumber = None,
  - top: OptionalNumber = None,
  - right: OptionalNumber = None,
  - bottom: OptionalNumber = None,
  - expand: Union[None, bool, int] = None,
  - col: Optional[ResponsiveNumber] = None,
  - opacity: OptionalNumber = None,
  - rotate: RotateValue = None,
  - scale: ScaleValue = None,
  - offset: OffsetValue = None,
  - aspect_ratio: OptionalNumber = None,
  - animate_opacity: AnimationValue = None,
  - animate_size: AnimationValue = None,
  - animate_position: AnimationValue = None,
  - animate_rotation: AnimationValue = None,
  - animate_scale: AnimationValue = None,
  - animate_offset: AnimationValue = None,
  - on_animation_end=None,
  - tooltip: Optional[str] = None,
  - visible: Optional[bool] = None,
  - disabled: Optional[bool] = None,
  - data: Any = None,

특화항목
  - color: Optional[str] = None,
  - bgcolor: Optional[str] = None,
  - elevation: OptionalNumber = None,
  - style: Optional[ButtonStyle] = None,
  - icon: Optional[str] = None,
  - icon_color: Optional[str] = None,
  - content: Optional[Control] = None,
  - autofocus: Optional[bool] = None,
  - url: Optional[str] = None,
  - url_target: Optional[str] = None,
  - on_click=None,
  - on_long_press=None,
  - on_hover=None,
  - on_focus=None,
  - on_blur=None,

### ft.FloatingActionButton
공통항목
   - ft.ElevatedButton 공통항목

특화항목
   - icon: Optional[str] = None,
   - bgcolor: Optional[str] = None,
   - content: Optional[Control] = None,
   - autofocus: Optional[bool] = None,
   - shape: Optional[OutlinedBorder] = None,
   - mini: Optional[bool] = None,
   - url: Optional[str] = None,
   - url_target: Optional[str] = None,
   - on_click=None,

### ft.FoamFieldControl
공통항목
   - ft.ConstrainedControl와 데이터 공통

특화항목
   - text_size: OptionalNumber = None,
   - text_style: Optional[TextStyle] = None,
   - label: Optional[str] = None,
   - label_style: Optional[TextStyle] = None,
   - icon: Optional[str] = None,
   - border: Optional[InputBorder] = None,
   - color: Optional[str] = None,
   - bgcolor: Optional[str] = None,
   - border_radius: BorderRadiusValue = None,
   - border_width: OptionalNumber = None,
   - border_color: Optional[str] = None,
   - focused_color: Optional[str] = None,
   - focused_bgcolor: Optional[str] = None,
   - focused_border_width: OptionalNumber = None,
   - focused_border_color: Optional[str] = None,
   - content_padding: PaddingValue = None,
   - dense: Optional[bool] = None,
   - filled: Optional[bool] = None,
   - hint_text: Optional[str] = None,
   - hint_style: Optional[TextStyle] = None,
   - helper_text: Optional[str] = None,
   - helper_style: Optional[TextStyle] = None,
   - counter_text: Optional[str] = None,
   - counter_style: Optional[TextStyle] = None,
   - error_text: Optional[str] = None,
   - error_style: Optional[TextStyle] = None,
   - prefix: Optional[Control] = None,
   - prefix_icon: Optional[str] = None,
   - prefix_text: Optional[str] = None,
   - prefix_style: Optional[TextStyle] = None,
   - suffix: Optional[Control] = None,
   - suffix_icon: Optional[str] = None,
   - suffix_text: Optional[str] = None,
   - suffix_style: Optional[TextStyle] = None,






